import subprocess
import os

import redis

from app import redis_connection_pool

redis = redis.Redis(connection_pool=redis_connection_pool)


class Sandbox:

    def __init__(self):
        self.box_id = None
        self.box_path = None
        self.files = set()
        self.dirs = set()

    def add_file_from_string(self, content, filename):
        filepath = os.path.join(self.box_path, filename)
        self.files.add(filename)
        with open(filepath, "w") as f:
            f.write(content)

    def add_dir(self, dir):
        self.dirs.add(dir)

    def init_isolate(self):
        self.box_id = get_redis_box_id()

        cmd = ["isolate", "-b", str(self.box_id), "--cg"]
        cmd.append("--init")

        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if p.returncode != 0:
            raise SandboxException(
                "Cannot init isolate ({})".format(p.stderr.decode()))

        self.box_path = os.path.join(p.stdout.decode().strip(), "box")

    def cleanup_isolate(self):
        cmd = ["isolate", "-b", str(self.box_id), "--cg"]
        cmd.append("--cleanup")

        p = subprocess.run(cmd, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

        if p.returncode != 0:
            raise SandboxException(
                "Cannot cleanup isolate ({})".format(p.stderr.decode()))

    def parse_meta(self):
        meta_path = os.path.join(self.box_path, "_isolate.meta")
        result = {}
        if os.path.isfile(meta_path):
            with open(meta_path) as f:
                for line in f:
                    key, val = line.split(":")
                    result[key] = val.strip()

        return result

    def _build_command(self, command, time_limit=None, memory_limit=None, stdin=None, stdout=None):
        base = ["isolate", "-b", str(self.box_id), "--cg"]

        for directory in self.dirs:
            base.append('--dir={}'.format(directory))

        base.append("--full-env")

        base.append("--cg-timing")
        base.append("--processes")

        if time_limit is not None:
            base.append("--time={}".format(time_limit))
            base.append("--wall-time={}".format(time_limit + 8))
            base.append("--extra-time=0.5")

        if memory_limit is not None:
            base.append("--cg-mem={}".format(memory_limit * 1024))
            base.append("--stack={}".format(memory_limit * 1024))

        if stdin is not None:
            base.append('--stdin={}'.format(stdin))

        if stdout is not None:
            base.append('--stdout={}'.format(stdout))

        meta_path = os.path.join(self.box_path, "_isolate.meta")
        base.append('--meta={}'.format(meta_path))

        base.append("--run")
        base.append("--")

        base.extend(command)

        return base


class JavaSandbox(Sandbox):

    def __init__(self):
        super().__init__()

    def compile(self, filename):
        compile_command = ["/bin/bash", "-c", "javac {}".format(filename)]
        cmd = self._build_command(compile_command)

        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return p.returncode, p.stderr.decode()

    def run_testcase(self, filename, time_limit, memory_limit, input_, output_):
        run_command = ["/bin/bash", "-c", "java {}".format(filename)]

        actual = "_output"
        cmd = self._build_command(
            run_command, time_limit, memory_limit, input_, actual)

        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = self.parse_meta()

        if p.returncode == 0:
            diff_command = ["/bin/bash", "-c",
                            "diff -Z {} {}".format(output_, actual)]
            cmd = self._build_command(diff_command)

            q = subprocess.run(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

            return "AC" if q.returncode == 0 else "WA", result["time"]

        else:
            status = {"RE": "RTE", "TO": "TLE", "SG": "XX", "XX": "XX"}
            return status[result["status"]], result["time"]


class SandboxException(Exception):
    pass


def get_redis_box_id():
    cmd = """
        local x = redis.call('INCRBY', KEYS[1], 1)
        local y = tonumber(ARGV[1])
        if x >= y then
            return redis.call('DECRBY', KEYS[1], y)
        end
        return x
    """
    num = redis.eval(cmd, 1, "_BOX_ID", 256)
    return num
