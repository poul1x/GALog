import os
import sys

SELF_FILE_PATH = "."
if sys.argv[0].endswith(".exe"):
    SELF_FILE_PATH = os.path.dirname(sys.argv[0])


def _resPathJoin(*args: str):
    return os.path.join(SELF_FILE_PATH, "res", *args)


FONTS_DIR = _resPathJoin("fonts")
STYLESHEET_DIR = _resPathJoin("styles", "auto")
HIGHLIGHTING_DIR = _resPathJoin("highlighting")


def styleSheetFile(name: str):
    return _resPathJoin("styles", "manual", name + ".qss")


def iconFile(name: str):
    return _resPathJoin("icons", name + ".svg")


def stringsFile(lang: str):
    return _resPathJoin("strings", lang + ".yaml")


def dirFilesRecursive(path: str, ext: str):
    result = []
    for entry in os.scandir(path):
        if entry.is_file() and entry.path.endswith(ext):
            result.append(entry.path)
        elif entry.is_dir():
            result.extend(dirFilesRecursive(entry.path, ext))

    return result


def highlightingFiles():
    return dirFilesRecursive(HIGHLIGHTING_DIR, ".yaml")


def styleSheetFiles():
    return dirFilesRecursive(STYLESHEET_DIR, ".qss")


def fontFiles():
    return dirFilesRecursive(FONTS_DIR, ".tar.xz")
