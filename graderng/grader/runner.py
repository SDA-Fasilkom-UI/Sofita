from grader.sandbox import JavaSandbox


class Runner():
    Sandbox = None

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
