from typing import List, Optional
from PyQt5.QtCore import QEvent, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from enum import Enum, auto


class ChangedEntry(int, Enum):
    AppSettings = auto()
    AppFontSettings = auto()
    AdvancedFilterSettings = auto()
    AdbServerSettings = auto()
    LastSelectedDevice = auto()
    LastSelectedPackage = auto()


def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class SettingsChangeNotifier(QObject):
    settingsChanged = pyqtSignal(ChangedEntry)

    def notify(self, entry: ChangedEntry):
        self.settingsChanged.emit(entry)