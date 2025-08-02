from typing import Optional
from PyQt5.QtCore import QThread, QCoreApplication
from galog.app import paths
import yaml
from .models import AppSettings, TagFilteringSettings
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


class AppSettingsProvider:
    _instance: Optional["AppSettingsProvider"] = None

    def __init__(self):
        self._configPath = paths.appConfigFile()
        self._loadSettingsFromFile()

    @mainThreadOnly
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(AppSettingsProvider, cls).__new__(cls)
        return cls._instance

    def _loadSettingsFromFile(self):
        with open(self._configPath, "r") as f:
            settings = AppSettings(**yaml.safe_load(f.read()))

        settings.lastSelectedDevice = None
        settings.lastSelectedPackage = None
        settings.lastUsedDirPath = ""

        if settings.advancedTagFilter is None:
            settings.advancedTagFilter = TagFilteringSettings.default()

        self._settings = settings

    def _saveSettingsToFile(self, settings: AppSettings):
        with open(self._configPath, "w") as f:
            f.write(yaml.dump(settings.model_dump()))

    @mainThreadOnly
    def settings(self):
        return self._settings

    @mainThreadOnly
    def saveSettings(self, settings: AppSettings):
        self._saveSettingsToFile(settings)
