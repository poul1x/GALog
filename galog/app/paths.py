import os
import sys
import logging
from datetime import datetime
from typing import Callable
from .random import randomSessionId

from PyQt5.QtCore import QStandardPaths





def _appDataReadOnlyDirs():
    return QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)


def _appDataRootDir():
    return QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)


def _appConfigRootDir():
    return QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)


_APP_NAME = "galog"
_APP_SESSION_ID = randomSessionId()
_APP_DATA_DIR = os.path.join(_appDataRootDir(), _APP_NAME)
_APP_CONFIG_DIR = os.path.join(_appConfigRootDir(), _APP_NAME)
_LOG = logging.getLogger("Paths")
_RES_DIR = "res"


def resDirPath(*args: str):
    return os.path.join(_RES_DIR, *args)


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


def appDataReadOnlyDir():
    # List of standard locations where read only data dir can be placed
    paths = [os.path.join(path, _APP_NAME) for path in _appDataReadOnlyDirs()]

    # If it's a portable version, try ./<res-dir> path
    paths.append(os.path.abspath(_RES_DIR))

    # Check directory exists at one of the paths
    for candidatePath in paths:
        if os.path.isdir(candidatePath):
            return candidatePath

    # Nothing found
    return None


def appLogsRootDir():
    return os.path.join(_APP_DATA_DIR, "logs")


def appLogsDir():
    return os.path.join(_APP_DATA_DIR, "logs", _APP_SESSION_ID)


def appSessionID():
    return _APP_SESSION_ID


def appConfigDir():
    return os.path.join("config")

def appConfigFile():
    return os.path.join(appConfigDir(), "galog.yaml")
