from functools import wraps
from typing import List, Optional

import yaml
from PyQt5.QtCore import QCoreApplication, QThread

from galog.app.paths import appConfigFile

from .models import AdvancedFilterSettings, AppSessionSettings, AppSettings


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


_sessionSettings: Optional[AppSessionSettings] = None
_settings: Optional[AppSettings] = None


@mainThreadOnly
def _loadSettingsFromFile():
    configPath = appConfigFile()
    with open(configPath, "r") as f:
        settings = AppSettings(**yaml.safe_load(f.read()))

    return settings


def _saveSettingsToFile(settings: AppSettings):
    configPath = appConfigFile()
    with open(configPath, "w") as f:
        settingsDict = settings.model_dump(mode="json")
        f.write(yaml.dump(settingsDict, sort_keys=False))


@mainThreadOnly
def readSettings():
    global _settings
    if _settings is None:
        _settings = _loadSettingsFromFile()

    assert isinstance(_settings, AppSettings)
    return _settings


@mainThreadOnly
def writeSettings(settings: AppSettings, reload: bool = False):
    correctSettings = AppSettings(**settings.model_dump())
    _saveSettingsToFile(correctSettings)

    if reload:
        global _settings
        _settings = None


@mainThreadOnly
def readSessionSettings():
    global _sessionSettings
    if _sessionSettings is None:
        _sessionSettings = AppSessionSettings.new()

    assert isinstance(_sessionSettings, AppSessionSettings)
    return _sessionSettings
