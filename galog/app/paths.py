import os
from typing import Callable

from PyQt5.QtCore import QStandardPaths

from .bootstrap import (
    APP_SESSION_ID,
    FONTS_DIR_NAME,
    HRULES_DIR_NAME,
    ICONS_DIR_NAME,
    IMAGES_DIR_NAME,
    LOGGING_CONFIG_FILE,
    LOGGING_DIR_NAME,
    MAIN_CONFIG_FILE,
    QSS_DIR_NAME,
    RES_DIR_NAME,
)


def _appDataRootDir():
    return QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)


def _appConfigRootDir():
    return QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)


_APP_NAME = "galog"
_APP_DATA_DIR = os.path.join(_appDataRootDir(), _APP_NAME)
# _APP_RES_DIR = os.path.join(_APP_DATA_DIR, RES_DIR_NAME)
_APP_RES_DIR = os.path.join(".", RES_DIR_NAME)
_APP_CONFIG_DIR = os.path.join(_appConfigRootDir(), _APP_NAME)


def _resDirJoin(*args: str):
    return os.path.join(_APP_RES_DIR, *args)


def _configDirJoin(*args: str):
    return os.path.join(_APP_CONFIG_DIR, *args)


def _appDataDirJoin(*args: str):
    return os.path.join(_APP_DATA_DIR, *args)


def styleSheetFile(name: str):
    return _resDirJoin(QSS_DIR_NAME, "manual", name + ".qss")


def iconFile(name: str):
    return _resDirJoin(ICONS_DIR_NAME, name + ".svg")


def imageFile(name: str):
    return _resDirJoin(IMAGES_DIR_NAME, name + ".png")


def dirFilesRecursive(path: str, fnFilter: Callable[[str], bool]):
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)
            if fnFilter(path):
                result.append(path)

    return result


def hRulesFiles():
    return dirFilesRecursive(
        _configDirJoin(HRULES_DIR_NAME),
        lambda path: path.endswith(".yaml"),
    )


def styleSheetFiles():
    return dirFilesRecursive(
        _resDirJoin(QSS_DIR_NAME, "auto"),
        lambda path: path.endswith(".qss"),
    )


def fontFiles():
    return dirFilesRecursive(
        _resDirJoin(FONTS_DIR_NAME),
        lambda path: path.endswith(".tar.xz"),
    )


def appDataDir():
    return _APP_DATA_DIR


def appConfigDir():
    return _APP_CONFIG_DIR


def appResDir():
    return _APP_RES_DIR


def appConfigFile():
    return _configDirJoin(MAIN_CONFIG_FILE)


def hRulesDir():
    return _configDirJoin(HRULES_DIR_NAME)


def loggingConfigFile():
    return _configDirJoin(LOGGING_CONFIG_FILE)


def loggingConfigFile():
    return _configDirJoin(LOGGING_CONFIG_FILE)


def appLogsRootDir():
    return _appDataDirJoin(LOGGING_DIR_NAME)


def appLogsDir():
    return _appDataDirJoin(LOGGING_DIR_NAME, APP_SESSION_ID)
