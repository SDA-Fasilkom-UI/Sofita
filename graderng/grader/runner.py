import concurrent.futures
import os

from django.conf import settings
from django.template import Context, Template

from grader.constants import (
    COMPILATION_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT,
    VERDICT_FEEDBACK
)
from grader.sandbox import JavaSandbox
from grader.utils import get_problems_path


class Runner():
    Sandbox = None

    def __init__(self, sub):
        self.sub = sub

    def _validate_and_get_cases_path(self):
        problems_path = get_problems_path()
        cases_path = os.path.join(
            problems_path, self.sub.problem_name, "cases")

        if not os.path.isdir(cases_path):
            return None

        files = os.listdir(cases_path)
        num_files = len(files)
        num_tc = num_files - num_files // 2  # handle odd num_files

        valid = True
        for i in range(1, num_tc + 1):
            in_filename = "{}.in".format(i)
            out_filename = "{}.out".format(i)

            if (in_filename not in files) or (out_filename not in files):
                valid = False
                break

        if not valid:
            return None

        return cases_path

    def _do_compile(self):
        try:
            sandbox = self.Sandbox()
            sandbox.init_isolate()

            sandbox.write_to_file(self.sub.content, self.sub.filename)
            compile_code, error, exec_name = sandbox.compile(self.sub.filename)

            if compile_code == 0:
                exec_path = os.path.join(sandbox.box_path, exec_name)
                with open(exec_path, "rb") as f:
                    exec_content = f.read()

                return (compile_code, error, exec_content, exec_name)

            return (compile_code, error, None, None)

        finally:
            sandbox.cleanup_isolate()

    def _do_run(self, exec_content, exec_name, cases_path, input_path, output_path):
        try:
            sandbox = self.Sandbox()
            sandbox.init_isolate()

            sandbox.mount_dir(cases_path)
            sandbox.write_to_file(exec_content, exec_name, binary=True)

            status, time = sandbox.run(
                exec_name,
                self.sub.time_limit,
                self.sub.memory_limit,
                input_path,
                output_path
            )

            return (status, time)

        finally:
            sandbox.cleanup_isolate()

    def grade_submission(self):
        if self.Sandbox is None:
            raise NotImplementedError("Sandbox not implemented")

        # validate cases_path
        cases_path = self._validate_and_get_cases_path()
        if cases_path is None:
            return (0, DIRECTORY_NOT_FOUND_OR_INVALID_ERROR, DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT)

        # compile
        compile_code, error, exec_content, exec_name = self._do_compile()
        if compile_code != 0:
            error_minimum = "\n".join(error.split("\n")[:20])
            return (0, self.render_html(COMPILATION_ERROR, {"error": error_minimum}), error_minimum)

        num_files = len(os.listdir(cases_path))
        num_tc = num_files // 2

        result = {}

        max_workers = settings.TESTCASE_CONCURRENCY
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_tc = {}
            for i in range(num_tc):

                future = executor.submit(
                    self._do_run,
                    exec_content,
                    exec_name,
                    cases_path,
                    os.path.join(cases_path, "{}.in".format(i + 1)),
                    os.path.join(cases_path, "{}.out".format(i + 1))
                )
                future_to_tc[future] = i

            for future in concurrent.futures.as_completed(future_to_tc):
                tc = future_to_tc[future]
                status, time = future.result()

                result[tc] = (status, time)

        verdict = []
        for i in range(num_tc):
            verdict.append(result[i])

        num_ac = len([x for x in verdict if x[0] == "AC"])
        grade = num_ac * 100 / len(verdict)

        feedback = self.render_html(VERDICT_FEEDBACK, {
            "grade": grade,
            "verdict": verdict
        })

        verdict_txt = self.verdict_to_text(verdict)

        return (grade, feedback, verdict_txt)

    def render_html(self, content, data):
        template = Template(content)
        context = Context(data)

        return template.render(context)

    def verdict_to_text(self, verdict):
        result = ""
        for i in range(len(verdict)):
            status, time = verdict[i]
            result += "{}: {} ({})".format(i + 1, status, time)
            result += "\n" if (i + 1) % 5 == 0 else " | "

        return result


class JavaRunner(Runner):
    Sandbox = JavaSandbox
