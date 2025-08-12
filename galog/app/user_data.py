import os
import shutil

from PyQt5.QtCore import QStandardPaths

from galog.app.bootstrap import (
    APP_NAME,
    CONFIG_DIR_NAME,
    DEPLOYMENT,
    HRULES_DIR_NAME,
    LOGGING_CONFIG_FILE,
    MAIN_CONFIG_FILE,
    RES_DIR_NAME,
    DeploymentMode,
)
from galog.app.paths import (
    appConfigDir,
    appConfigFile,
    appDataDir,
    appResDir,
    hRulesDir,
    loggingConfigFile,
)


def _appDataReadOnlyDirs():
    return QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)


def _appDataReadOnlyDir():
    if DEPLOYMENT == DeploymentMode.Portable:
        return os.path.abspath(os.curdir)

    for dirPath in _appDataReadOnlyDirs():
        absDirPath = os.path.abspath(dirPath)
        candidatePath = os.path.join(absDirPath, APP_NAME)
        if os.path.isdir(candidatePath):
            return candidatePath

    return None


def initializeUserData():
    dataDir = _appDataReadOnlyDir()
    if dataDir is None:
        raise RuntimeError("Read-only AppData directory not found")

    resDir = os.path.join(dataDir, RES_DIR_NAME)
    if not os.path.exists(resDir):
        raise RuntimeError("Read-only 'res' directory not found")

    configDir = os.path.join(dataDir, CONFIG_DIR_NAME)
    if not os.path.exists(configDir):
        raise RuntimeError("Read-only 'config' directory not found")

    userDataDir = appDataDir()
    os.makedirs(userDataDir, exist_ok=True)

    userConfigDir = appConfigDir()
    os.makedirs(userConfigDir, exist_ok=True)

    resUserDir = appResDir()
    if not os.path.exists(resUserDir):
        shutil.copytree(resDir, resUserDir)

    configUserFile = appConfigFile()
    if not os.path.exists(configUserFile):
        configFile = os.path.join(configDir, MAIN_CONFIG_FILE)
        shutil.copy(configFile, configUserFile)

    logingConfigUserFile = loggingConfigFile()
    if not os.path.exists(logingConfigUserFile):
        _loggingConfigFile = os.path.join(configDir, LOGGING_CONFIG_FILE)
        shutil.copy(_loggingConfigFile, logingConfigUserFile)

    hRulesUserDir = hRulesDir()
    if not os.path.exists(hRulesUserDir):
        _hRulesDir = os.path.join(configDir, HRULES_DIR_NAME)
        shutil.copytree(_hRulesDir, hRulesUserDir)
