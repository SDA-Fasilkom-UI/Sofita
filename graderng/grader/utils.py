import os

from filebrowser.sites import site


def get_problems_path():
    location = site.storage.location
    directory = site.directory
    return os.path.join(location, directory)
