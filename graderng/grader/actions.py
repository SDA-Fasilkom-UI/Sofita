import io
import os
import shutil
import zipfile

from django.contrib import messages
from django.http import HttpResponse
from filebrowser.sites import site
from filebrowser.utils import convert_filename


def register_actions():
    """
    Register actions, make sure to called it once.
    """

    site.add_action(validate_and_extract_zip)
    site.add_action(zip_and_download_folder)


def zip_and_download_folder(request, fileobjects):
    fileobject = fileobjects[0]
    zipname = fileobject.filename + ".zip"

    buf = io.BytesIO()
    zipf = zipfile.ZipFile(buf, 'a', zipfile.ZIP_DEFLATED, False)

    for root, _, files in os.walk(fileobject.path_full):
        for file_ in files:
            fileabspath = os.path.join(root, file_)
            filerelpath = os.path.relpath(fileabspath, site.storage.location)
            arcname = os.path.relpath(filerelpath, fileobject.head)

            zipf.write(fileabspath, arcname)

    zipf.close()

    # Can't use FileResponse, it is not subclass of HttpResponse
    response = HttpResponse(buf.getvalue(), content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename="%s"' % zipname
    return response


def validate_and_extract_zip(request, fileobjects):
    fileobject = fileobjects[0]

    if not zipfile.is_zipfile(fileobject.path_full):
        show_error(request, "File is not a zip file")
        return

    with zipfile.ZipFile(fileobject.path_full) as filezip:
        zip_ok = True
        try:
            zip_ok = (filezip.testzip() is None)
        except RuntimeError:
            zip_ok = False

        if not zip_ok:
            show_error(request, "File is corrupted or encrypted")
            return

        info_list = filezip.infolist()
        dirs = {"/": set()}
        cnt_dir = 0
        for info in info_list:
            if info.is_dir():
                dirs[info.filename] = set()
                parent_dir = os.path.dirname(info.filename[:-1]) + "/"

                dirs[parent_dir].add(info.filename)
                if parent_dir == "/":
                    cnt_dir += 1
            else:
                parent_dir = os.path.dirname(info.filename) + "/"
                dirs[parent_dir].add(info.filename)

        if cnt_dir != 1:
            show_error(request, "File must contains one directory")
            return

        problem_path = list(dirs["/"])[0]
        cases_path = os.path.join(problem_path, "cases/")

        if cases_path not in dirs[problem_path]:
            show_error(request, "'cases/' folder not found")
            return

        dir_len = len(dirs[cases_path])
        tc_len = dir_len - dir_len // 2

        valid = True
        for i in range(1, tc_len + 1):
            input_ = os.path.join(cases_path, str(i) + ".in")
            output_ = os.path.join(cases_path, str(i) + ".out")

            if input_ not in dirs[cases_path]:
                show_error(request, input_ + " not found")
                valid = False

            if output_ not in dirs[cases_path]:
                show_error(request, output_ + " not found")
                valid = False

        if not valid:
            show_error(request, "No additional file allowed in 'cases'")
            return

        location = site.storage.location
        directory = site.directory
        path = os.path.join(location, directory)

        for info in info_list:
            name = convert_filename(info.filename)
            filepath = os.path.join(path, name)

            if info.is_dir():
                if os.path.isdir(filepath):
                    shutil.rmtree(filepath)
                os.mkdir(filepath)
            else:
                content = filezip.read(info)
                with open(filepath, "wb") as f:
                    f.write(content)

        show_success(request, "Extracted")


validate_and_extract_zip.applies_to = (
    lambda fileobject: fileobject.extension == ".zip")

zip_and_download_folder.applies_to = (
    lambda fileobject: fileobject.filetype == "Folder"
)


def show_error(request, msg):
    messages.add_message(request, messages.ERROR, msg)


def show_success(request, msg):
    messages.add_message(request, messages.SUCCESS, msg)
