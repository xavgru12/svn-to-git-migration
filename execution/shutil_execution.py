import shutil
import os
import stat


def extract(zip_file, destination):
    shutil.unpack_archive(zip_file, destination)
    os.remove(zip_file)


def delete(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory, onexc=on_remove_error)


def on_remove_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)
