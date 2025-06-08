import os
import sys
import random
import logging
from datetime import datetime
from typing import Callable

from PyQt5.QtCore import QStandardPaths

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


if not sys.argv[0].endswith(".py"):
    os.chdir(os.path.dirname(sys.argv[0]))


def _appDataRootDir():
    path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    return os.path.normpath(path)



_APP_NAME = "galog"
_APP_SESSION_ID = _generateSessionId()
_APP_DATA_DIR = os.path.join(_appDataRootDir(), _APP_NAME)
_LOG = logging.getLogger("Paths")


def resDirPath(*args: str):
    return os.path.join("res", *args)


def _appDataRelativePath(*args: str):
    return os.path.join(_APP_DATA_DIR, *args)


def styleSheetFile(name: str):
    return resDirPath("qss", "manual", name + ".qss")


def iconFile(name: str):
    return resDirPath("icons", name + ".svg")


def imageFile(name: str):
    return resDirPath("images", name + ".png")


def loggingConfigFileInitial():
    return resDirPath("logging", "logging.yaml")


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
        resDirPath("highlighting"),
        lambda path: path.endswith(".yaml"),
    )


def styleSheetFiles():
    return dirFilesRecursive(
        resDirPath("qss", "auto"),
        lambda path: path.endswith(".qss"),
    )


def fontFiles():
    return dirFilesRecursive(
        resDirPath("fonts"),
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


def appSessionID():
    return _APP_SESSION_ID


def appConfigDir():
    return os.path.join(_APP_DATA_DIR, "config")
