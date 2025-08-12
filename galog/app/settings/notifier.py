from enum import Enum, auto

from PyQt5.QtCore import QObject, pyqtSignal


class ChangedEntry(int, Enum):
    AppSettings = auto()
    AppFontSettingsStandard = auto()
    AppFontSettingsLogViewer = auto()
    AppFontSettingsMenuBar = auto()
    AdvancedFilterSettings = auto()
    AdbServerSettings = auto()
    LastSelectedDevice = auto()
    LastSelectedPackage = auto()
    LiveReload = auto()
    TextHighlighting = auto()
    ShowLineNumbers = auto()


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
