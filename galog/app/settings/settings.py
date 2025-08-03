from contextlib import contextmanager
from typing import Optional
from PyQt5.QtCore import QThread, QCoreApplication
from galog.app.paths import appConfigFile
import yaml
from .models import AppSettings, AdvancedFilterSettings
from functools import wraps


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


@mainThreadOnly
def _loadSettingsFromFile():
    configPath = appConfigFile()
    with open(configPath, "r") as f:
        settings = AppSettings(**yaml.safe_load(f.read()))

    settings.lastSelectedDevice = None
    settings.lastSelectedPackage = None
    settings.advancedFilter = AdvancedFilterSettings.default()
    settings.lastUsedDirPath = ""
    return settings


def _saveSettingsToFile(settings: AppSettings):
    exclude = {
        "lastSelectedDevice",
        "lastSelectedPackage",
        "advancedTagFilter",
        "lastUsedDirPath",
    }

    configPath = appConfigFile()
    with open(configPath, "w") as f:
        f.write(yaml.dump(settings.model_dump(exclude=exclude)))


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
