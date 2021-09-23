import gzip
import io
import os
import traceback

from django.template import Context, Template
from filebrowser.sites import site


def render_html(content, data):
    template = Template(content)
    context = Context(data)

    return template.render(context)


def verdict_to_text(verdict):
    result = ""
    for i in range(len(verdict)):
        status, time = verdict[i]
        result += "{}: {} ({})".format(i + 1, status, time)
        result += "\n" if (i + 1) % 5 == 0 else " | "

    return result


def compress_gzip_file(path):
    buf = io.BytesIO()
    with open(path, "rb") as f, gzip.open(buf, "wb") as g:
        g.write(f.read())

    return buf.getvalue()


def decompress_gzip_file(val):
    buf = io.BytesIO(val)
    with gzip.open(buf, "rb") as g:
        return g.read().decode()


def validate_cases_path(problem_name):
    """
    return boolean indicating if cases path is valid
    """
    cases_path = get_cases_path(problem_name)
    if not os.path.isdir(cases_path):
        return False

    files = os.listdir(cases_path)
    num_files = len(files)
    num_tc = num_files - num_files // 2  # handle odd num_files

    for i in range(1, num_tc + 1):
        in_name, out_name = get_in_out_name(i)

        if (in_name not in files) or (out_name not in files):
            return False

    return True


def get_problems_path():
    """
    return problems path
    """
    location = site.storage.location
    directory = site.directory
    return os.path.join(location, directory)


def get_cases_path(problem_name):
    """
    return cases path
    """
    problems_path = get_problems_path()
    cases_path = os.path.join(problems_path, problem_name, "cases")
    return cases_path


def get_tc_path(problem_name, tc):
    """
    return pair of testcase path in and out (1-based)
    """
    cases_path = get_cases_path(problem_name)

    in_name, out_name = get_in_out_name(tc)
    in_path = os.path.join(cases_path, in_name)
    out_path = os.path.join(cases_path, out_name)
    return in_path, out_path


def get_num_tc(problem_name):
    """
    return num tc, raise error if cases path not found
    """
    files = os.listdir(get_cases_path(problem_name))
    return len(files) // 2


def get_tc_mtime(problem_name, tc):
    """
    return testcase modified time, raise error if not found (1-based)
    """
    in_path, out_path = get_tc_path(problem_name, tc)
    in_mtime = os.path.getmtime(in_path)
    out_mtime = os.path.getmtime(out_path)
    return int(max(in_mtime, out_mtime))


def get_in_out_name(num):
    """
    return pair in and out filename based on testcase number (1-based)
    """
    return str(num) + ".in", str(num) + ".out"


def get_traceback(exc):
    """
    hacky way to get traceback from exception
    """
    try:
        raise exc
    except:
        return traceback.format_exc(10)


class InputOutputNotFoundException(Exception):
    pass
