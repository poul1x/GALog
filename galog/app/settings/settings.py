from functools import wraps
from typing import List, Optional

import yaml
from PyQt5.QtCore import QCoreApplication, QThread

from galog.app.paths import appConfigFile

from .models import AdvancedFilterSettings, AppSettings


def mainThreadOnly(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        currentThread = QThread.currentThread()
        mainThread = QCoreApplication.instance().thread()
        if currentThread != mainThread:
            msg1 = f"Method '{func.__name__}' must be called from main thread"
            msg2 = f"Current thread: '{currentThread.objectName()}'"
            raise RuntimeError(f"{msg1}. {msg2}")

        return func(*args, **kwargs)

    return wrapper


_settings: Optional[AppSettings] = None


def _setDefaultValues(settings: AppSettings):
    settings.lastSelectedDevice = None
    settings.lastSelectedPackage = None
    settings.advancedFilter = AdvancedFilterSettings.default()
    settings.lastUsedDirPath = ""


@mainThreadOnly
def _loadSettingsFromFile():
    configPath = appConfigFile()
    with open(configPath, "r") as f:
        settings = AppSettings(**yaml.safe_load(f.read()))

    _setDefaultValues(settings)
    return settings


def _saveSettingsToFile(settings: AppSettings):
    configPath = appConfigFile()
    with open(configPath, "w") as f:
        _setDefaultValues(settings)
        settingsDict = settings.model_dump(mode="json")
        f.write(yaml.dump(settingsDict))


@mainThreadOnly
def reloadSettings():
    global _settings
    _settings = _loadSettingsFromFile()


@mainThreadOnly
def readSettings():
    if _settings is None:
        reloadSettings()

    assert isinstance(_settings, AppSettings)
    return _settings


@mainThreadOnly
def writeSettings(settings: AppSettings):
    correctSettings = AppSettings(**settings.model_dump())
    _saveSettingsToFile(correctSettings)
