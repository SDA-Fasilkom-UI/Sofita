import os

from django.template import Context, Template

from grader.constants import (
    COMPILATION_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR,
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

    def grade_submission(self):
        if self.Sandbox is None:
            raise NotImplementedError("Sandbox not implemented")

        try:
            sandbox = self.Sandbox()
            sandbox.init_isolate()

            # add submission
            sandbox.add_file_from_string(self.sub.content, self.sub.filename)

            # compile submission
            compile_code, error = sandbox.compile(self.sub.filename)
            if compile_code != 0:
                return (0, self.render_html(COMPILATION_ERROR, {"error": error}))

            # validate and add cases path to sandbox
            cases_path = self._validate_and_get_cases_path()
            if cases_path is None:
                return (0, DIRECTORY_NOT_FOUND_OR_INVALID_ERROR)
            sandbox.add_dir(cases_path)

            # run submission
            num_files = len(os.listdir(cases_path))
            num_tc = num_files // 2

            filename, _ = os.path.splitext(self.sub.filename)
            time_limit = self.sub.time_limit
            memory_limit = self.sub.memory_limit

            verdict = []
            for i in range(1, num_tc + 1):
                input_path = os.path.join(cases_path, "{}.in".format(i))
                output_path = os.path.join(cases_path, "{}.out".format(i))

                status, time = sandbox.run(
                    filename,
                    time_limit,
                    memory_limit,
                    input_path,
                    output_path
                )
                verdict.append((status, time))

            num_ac = len([x for x in verdict if x[0] == "AC"])
            grade = num_ac * 100 / len(verdict)

            feedback = self.render_html(VERDICT_FEEDBACK, {
                "grade": grade,
                "verdict": verdict
            })

            return (grade, feedback)

        finally:
            sandbox.cleanup_isolate()

    def render_html(self, content, data):
        template = Template(content)
        context = Context(data)

        return template.render(context)


class JavaRunner(Runner):
    Sandbox = JavaSandbox
