import os
import platform
import sys
from enum import Enum, auto

from galog.app.random import randomSessionId

APP_NAME = "galog"
APP_SESSION_ID = randomSessionId()
OS_NAME = platform.system()

RES_DIR_NAME = "res"
CONFIG_DIR_NAME = "config"
HRULES_DIR_NAME = "hrules"
LOGGING_DIR_NAME = "logs"
QSS_DIR_NAME = "qss"
FONTS_DIR_NAME = "fonts"
ICONS_DIR_NAME = "icons"
IMAGES_DIR_NAME = "images"
MAIN_CONFIG_FILE = "galog.yaml"
LOGGING_CONFIG_FILE = "logging.yaml"


class RuntimeEnvironment(int, Enum):
    PythonModule = auto()
    PyInstaller = auto()


class DeploymentMode(int, Enum):
    Portable = auto()
    Installer = auto()


def _runtimeEnvironment():
    if sys.argv[0].endswith(".py"):
        return RuntimeEnvironment.PythonModule
    else:
        return RuntimeEnvironment.PyInstaller


def _deploymentMode():
    if os.path.exists(RES_DIR_NAME):
        return DeploymentMode.Portable
    else:
        return DeploymentMode.Installer


RUNTIME = _runtimeEnvironment()
DEPLOYMENT = _deploymentMode()
