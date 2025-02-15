import os
import sys
from typing import Callable
from PyQt5.QtCore import QStandardPaths

from datetime import datetime
import random

# Initialize pseudorandom sequences
random.seed(datetime.now().timestamp())


def randomDigit():
    return str(random.randint(0, 9))


def randomChar():
    return random.choice("abcdefghijklmnopqrstuvwxyz")

def _generateSessionId():
    return "{}-{}".format(
        datetime.now().replace(microsecond=0).isoformat().replace(":", "-"),
        randomChar() + randomDigit() + randomChar() + randomDigit(),
    )


SELF_FILE_PATH = "."
if not sys.argv[0].endswith(".py"):
    SELF_FILE_PATH = os.path.dirname(sys.argv[0])


def _appDataRootDir():
    return QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)


_APP_NAME = "GALog"
_APP_SESSION_ID = _generateSessionId()
_APP_DATA_DIR = os.path.join(_appDataRootDir(), _APP_NAME)


def _selfRelativePath(*args: str):
    return os.path.join(SELF_FILE_PATH, "res", *args)


def _appDataRelativePath(*args: str):
    return os.path.join(_APP_DATA_DIR, *args)


def styleSheetFile(name: str):
    return _selfRelativePath("styles", "manual", name + ".qss")


def iconFile(name: str):
    return _selfRelativePath("icons", name + ".svg")


def loggingConfigFileInitial():
    return _selfRelativePath("logging", "logging.yaml")


def loggingConfigFile():
    return _appDataRelativePath("config", "logging.yaml")


def dirFilesRecursive(path: str, fnFilter: Callable[[str], bool]):
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)
            if fnFilter(path):
                result.append(path)

    return result


def highlightingFiles():
    return dirFilesRecursive(
        _selfRelativePath("highlighting"),
        lambda path: path.endswith(".yaml"),
    )


def styleSheetFiles():
    return dirFilesRecursive(
        _selfRelativePath("styles", "auto"),
        lambda path: path.endswith(".qss"),
    )


def fontFiles():
    return dirFilesRecursive(
        _selfRelativePath("fonts"),
        lambda path: path.endswith(".tar.xz"),
    )


def appName():
    return _APP_NAME


def appDataDir():
    return _APP_DATA_DIR

def appLogsRootDir():
    return os.path.join(_APP_DATA_DIR, "logs")

def appLogsDir():
    return os.path.join(_APP_DATA_DIR, "logs", _APP_SESSION_ID)


def appConfigDir():
    return os.path.join(_APP_DATA_DIR, "config")
