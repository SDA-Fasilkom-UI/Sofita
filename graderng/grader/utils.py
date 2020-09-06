import gzip
import io
import os

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


def get_problems_path():
    location = site.storage.location
    directory = site.directory
    return os.path.join(location, directory)


def get_tc_path(cases_path, tc):
    in_path = os.path.join(cases_path, str(tc+1) + ".in")
    out_path = os.path.join(cases_path, str(tc+1) + ".out")
    return in_path, out_path


class InputOutputNotFoundException(Exception):
    pass
