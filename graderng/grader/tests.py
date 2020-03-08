import fakeredis

from unittest import mock

from django.test import TestCase

from grader import sandbox


class SandboxTest(TestCase):
    meta_data = \
        """

          status: XX
        time:3.54

        """

    def setUp(self):
        self.base_sandbox = sandbox.Sandbox()
        self.fake_redis = fakeredis.FakeStrictRedis()

    @mock.patch("grader.sandbox.redis")
    def test_get_redis_box_id(self, mock_redis):
        mock_redis.eval = self.fake_redis.eval
        for i in range(1, 256):
            self.assertEqual(i, sandbox.get_redis_box_id())
        self.assertEqual(0, sandbox.get_redis_box_id())
        self.assertEqual(1, sandbox.get_redis_box_id())

    @mock.patch("grader.sandbox.get_redis_box_id")
    @mock.patch("grader.sandbox.subprocess")
    def test_init_isolate(self, mock_subprocess, mock_redis):
        subprocess_res = mock.Mock()
        subprocess_run = mock.Mock()

        subprocess_res.returncode = 1
        subprocess_run.return_value = subprocess_res

        mock_redis.return_value = 137
        mock_subprocess.run = subprocess_run
        self.assertRaises(sandbox.SandboxException,
                          self.base_sandbox.init_isolate)

        subprocess_res.returncode = 0
        subprocess_res.stdout = b"/path/to/box-dir"
        subprocess_run.return_value = subprocess_res
        command = ['isolate', '-b', '137', '--cg', '--init']

        mock_subprocess.run = subprocess_run
        self.base_sandbox.init_isolate()
        self.assertListEqual(command, subprocess_run.call_args[0][0])
        self.assertEqual(137, self.base_sandbox.box_id)
        self.assertEqual("/path/to/box-dir/box", self.base_sandbox.box_path)

    @mock.patch("grader.sandbox.subprocess")
    def test_cleanup_isolate(self, mock_subprocess):
        self.base_sandbox.box_id = 155

        subprocess_res = mock.Mock()
        subprocess_run = mock.Mock()

        subprocess_res.returncode = 1
        subprocess_run.return_value = subprocess_res

        mock_subprocess.run = subprocess_run
        self.assertRaises(sandbox.SandboxException,
                          self.base_sandbox.cleanup_isolate)

        subprocess_res.returncode = 0
        subprocess_run.return_value = subprocess_res
        command = ['isolate', '-b', '155', '--cg', '--cleanup']

        mock_subprocess.run = subprocess_run
        self.base_sandbox.cleanup_isolate()
        self.assertListEqual(command, subprocess_run.call_args[0][0])

    def test_build_command(self):
        self.base_sandbox.box_path = "/path/to/box-dir/box"
        self.base_sandbox.box_id = 198

        command = ['isolate', '-b', '198', '--cg', '--full-env', '--cg-timing',
                   '--processes', '--meta=/path/to/box-dir/box/_isolate.meta', '--run', '--']
        self.assertListEqual(command, self.base_sandbox._build_command([]))

        additional_command = ["/bin/bash", "abc"]

        self.base_sandbox.add_dir("/tmp/to/case")
        command = ['isolate', '-b', '198', '--cg', '--dir=/tmp/to/case', '--full-env', '--cg-timing',
                   '--processes', '--meta=/path/to/box-dir/box/_isolate.meta', '--run', '--',
                   '/bin/bash', 'abc']
        self.assertListEqual(
            command, self.base_sandbox._build_command(additional_command))

        command = ['isolate', '-b', '198', '--cg', '--dir=/tmp/to/case', '--full-env', '--cg-timing',
                   '--processes', '--time=3', '--wall-time=11', '--extra-time=0.5',
                   '--meta=/path/to/box-dir/box/_isolate.meta', '--run', '--', '/bin/bash', 'abc']
        self.assertListEqual(
            command, self.base_sandbox._build_command(additional_command, time_limit=3))

        command = ['isolate', '-b', '198', '--cg', '--dir=/tmp/to/case', '--full-env', '--cg-timing',
                   '--processes', '--cg-mem=262144', '--stack=262144',
                   '--meta=/path/to/box-dir/box/_isolate.meta', '--run', '--', '/bin/bash', 'abc']
        self.assertListEqual(
            command, self.base_sandbox._build_command(additional_command, memory_limit=256))

        command = ['isolate', '-b', '198', '--cg', '--dir=/tmp/to/case', '--full-env', '--cg-timing',
                   '--processes', '--stdin=/path/to/stdin',
                   '--meta=/path/to/box-dir/box/_isolate.meta', '--run', '--', '/bin/bash', 'abc']
        self.assertListEqual(
            command, self.base_sandbox._build_command(additional_command, stdin='/path/to/stdin'))

        command = ['isolate', '-b', '198', '--cg', '--dir=/tmp/to/case', '--full-env', '--cg-timing',
                   '--processes', '--stdout=/path/to/stdout',
                   '--meta=/path/to/box-dir/box/_isolate.meta', '--run', '--', '/bin/bash', 'abc']
        self.assertListEqual(
            command, self.base_sandbox._build_command(additional_command, stdout='/path/to/stdout'))

    def test_add_dir(self):
        self.base_sandbox.add_dir("problem/case")

        self.assertEqual(1, len(self.base_sandbox.dirs))
        self.assertEqual("problem/case", min(self.base_sandbox.dirs))

    @mock.patch("grader.sandbox.open", new_callable=mock.mock_open)
    def test_add_file_from_string(self, mock_open):
        mock_open.write = mock.Mock()

        self.base_sandbox.box_path = '/path/to/box-dir/box/'
        self.base_sandbox.add_file_from_string("abc", "file_abc")

        self.assertEqual(1, len(self.base_sandbox.files))
        self.assertEqual("file_abc", min(self.base_sandbox.files))
        self.assertEqual("/path/to/box-dir/box/file_abc",
                         mock_open.call_args[0][0])

    @mock.patch("grader.sandbox.os.path.isfile")
    @mock.patch("grader.sandbox.open", new_callable=mock.mock_open, read_data=meta_data)
    def test_parse_meta(self, mock_open, mock_path_isfile):
        self.base_sandbox.box_path = '/path/to/box-dir/box/'

        mock_path_isfile.return_value = False
        self.assertDictEqual({"time": -1.0}, self.base_sandbox.parse_meta())
        self.assertEqual("/path/to/box-dir/box/_isolate.meta",
                         mock_path_isfile.call_args[0][0])

        mock_path_isfile.return_value = True
        self.assertDictEqual({
            "status": "XX", "time": 3.54},
            self.base_sandbox.parse_meta()
        )

    @mock.patch("grader.sandbox.subprocess")
    def test_diff_ignore_whitespace(self, mock_subprocess):
        self.base_sandbox._build_command = (lambda x: x)

        subprocess_res = mock.Mock()
        subprocess_run = mock.Mock()

        subprocess_res.returncode = 1
        subprocess_run.return_value = subprocess_res
        command = ["/bin/bash", "-c", "diff -Z /path/to/file1 /path/to/file2"]

        mock_subprocess.run = subprocess_run
        ret = self.base_sandbox.diff_ignore_whitespace(
            "/path/to/file1", "/path/to/file2")
        self.assertFalse(ret)
        self.assertListEqual(command, subprocess_run.call_args[0][0])

        subprocess_res.returncode = 0
        subprocess_run.return_value = subprocess_res

        mock_subprocess.run = subprocess_run
        ret = self.base_sandbox.diff_ignore_whitespace(
            "/path/to/file1", "/path/to/file2")
        self.assertTrue(ret)


class JavaSandboxTest(TestCase):
    def setUp(self):
        self.java_sandbox = sandbox.JavaSandbox()

    @mock.patch("grader.sandbox.subprocess")
    def test_compile(self, mock_subprocess):
        self.java_sandbox._build_command = (lambda x: x)

        subprocess_res = mock.Mock()
        subprocess_run = mock.Mock()

        subprocess_res.returncode = 1
        subprocess_res.stderr = b"error"
        subprocess_run.return_value = subprocess_res
        command = ["/bin/bash", "-c", "javac Test.java"]

        mock_subprocess.run = subprocess_run
        ret_code, err = self.java_sandbox.compile("Test.java")
        self.assertEqual((1, "error"), (ret_code, err))
        self.assertListEqual(command, subprocess_run.call_args[0][0])

        subprocess_res.returncode = 0
        subprocess_res.stderr = b""
        subprocess_run.return_value = subprocess_res
        mock_subprocess.run = subprocess_run
        ret_code, err = self.java_sandbox.compile("Test.java")
        self.assertEqual((0, ""), (ret_code, err))

    @mock.patch("grader.sandbox.subprocess")
    @mock.patch("grader.sandbox.Sandbox.diff_ignore_whitespace")
    def test_run(self, mock_diff, mock_subprocess):
        self.java_sandbox._build_command = (
            lambda *args, **kwargs: args[0])

        subprocess_res = mock.Mock()
        subprocess_run = mock.Mock()

        subprocess_res.returncode = 1
        subprocess_run.return_value = subprocess_res
        command = ["/bin/bash", "-c", "java Test.java"]

        mock_subprocess.run = subprocess_run

        self.java_sandbox.parse_meta = (lambda: {"status": "RE", "time": 0.12})
        status, time = self.java_sandbox.run(
            "Test.java", 2, 256, "/path/to/input", "/path/to/output")
        self.assertEqual(("RTE", 0.12), (status, time))
        self.assertListEqual(command, subprocess_run.call_args[0][0])

        subprocess_res.returncode = 0
        subprocess_run.return_value = subprocess_res
        command = ["/bin/bash", "-c", "java Test.java"]

        mock_subprocess.run = subprocess_run

        self.java_sandbox.parse_meta = (lambda: {"time": 0.34})
        mock_diff.return_value = False
        status, time = self.java_sandbox.run(
            "Test.java", 2, 256, "/path/to/input", "/path/to/output")
        self.assertEqual(("WA", 0.34), (status, time))

        self.java_sandbox.parse_meta = (lambda: {"time": 0.54})
        mock_diff.return_value = True
        status, time = self.java_sandbox.run(
            "Test.java", 2, 256, "/path/to/input", "/path/to/output")
        self.assertEqual(("AC", 0.54), (status, time))
