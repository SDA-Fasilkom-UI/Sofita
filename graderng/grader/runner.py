import os


from grader.sandbox import JavaSandbox
from grader.utils import get_problems_path


class Runner():
    Sandbox = None

    @staticmethod
    def validate_and_get_cases_path(problem_name):
        problems_path = get_problems_path()
        cases_path = os.path.join(
            problems_path, problem_name, "cases")

        if not os.path.isdir(cases_path):
            return None, None

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
            return None, None

        return cases_path, num_tc

    @classmethod
    def compile(cls, content, filename):
        if cls.Sandbox is None:
            raise NotImplementedError("Sandbox not implemented")

        try:
            sandbox = cls.Sandbox()
            sandbox.init_isolate()

            sandbox.write_to_file(content, filename)
            return sandbox.compile(filename)

        finally:
            sandbox.cleanup_isolate()

    @classmethod
    def run(cls, exec_content, exec_name, time_limit, memory_limit, input_text, output_text):
        if cls.Sandbox is None:
            raise NotImplementedError("Sandbox not implemented")

        try:
            sandbox = cls.Sandbox()
            sandbox.init_isolate()

            input_filename = "input.txt"
            output_filename = "output.txt"

            sandbox.write_to_file(input_text, input_filename)
            sandbox.write_to_file(output_text, output_filename)
            sandbox.write_to_file(exec_content, exec_name, binary=True)

            return sandbox.run(
                exec_name,
                time_limit,
                memory_limit,
                input_filename,
                output_filename
            )

        finally:
            sandbox.cleanup_isolate()


class JavaRunner(Runner):
    Sandbox = JavaSandbox
