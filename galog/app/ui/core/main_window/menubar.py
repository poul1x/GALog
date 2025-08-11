import platform
from typing import List

from PyQt5.QtWidgets import QApplication, QMenu
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QMenuBar, QWidget
from galog.app.bootstrap import OS_NAME
from galog.app.settings import readSettings
from galog.app.settings.models import FontSettings
from galog.app.settings.notifier import ChangedEntry, SettingsChangeNotifier


class GALogMenuBar(QMenuBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._reloadSettings()
        self._subscribeForSettingsChanges()

    def _reloadSettings(self):
        self._settings = readSettings()

    def _settingsChanged(self, changedEntry: ChangedEntry):
        self._reloadSettings()
        if changedEntry == ChangedEntry.AppFontSettingsMenuBar:
            self._applyFontSettings()

    def _applyFontSettings(self):
        font = self._settings.fonts.menuBar
        self.setFont(QFont(font.family, font.size))

        titles = [
            self._menuTitleCapture(),
            self._menuTitleTools(),
            "",  # The last menu
        ]

        for i, menu in enumerate(self.findChildren(QMenu)):
            menu.setTitle(titles[i])

        self.update()

    def _subscribeForSettingsChanges(self):
        notifier = SettingsChangeNotifier()
        notifier.settingsChanged.connect(self._settingsChanged)

    def _menuTitleCapture(self):
        name = "&Capture"
        if self._settings.fonts.emojiEnabled:
            if self._settings.fonts.emojiAddSpace:
                return f"📱 {name}"
            else:
                return f"📱{name}"
        else:
            return name

    def _menuTitleTools(self):
        name = "&Tools"
        if self._settings.fonts.emojiEnabled:
            if self._settings.fonts.emojiAddSpace:
                return f"🛠 {name}"
            else:
                return f"🛠{name}"
        else:
            return name

    def addCaptureMenu(self):
        return self.addMenu(self._menuTitleCapture())

    def addToolsMenu(self):
        return self.addMenu(self._menuTitleTools())
