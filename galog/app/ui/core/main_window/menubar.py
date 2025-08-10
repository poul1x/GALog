import platform
from typing import List

from PyQt5.QtWidgets import QApplication
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
        self._hasEmojiFont = False
        self._setEmojiFontIfAvailable()
        self._subscribeForSettingsChanges()

    def _reloadSettings(self):
        self._settings = readSettings()

    def _settingsChanged(self, changedEntry: ChangedEntry):
        self._reloadSettings()
        if changedEntry == ChangedEntry.AppFontSettingsEmoji:
            self._applyFontSettings()

    def _applyFontSettings(self):
        font = self._settings.fonts.emoji
        self._setEmojiFont(font.family, font.size)
        self.update()
        # QApplication.processEvents()

    def _subscribeForSettingsChanges(self):
        notifier = SettingsChangeNotifier()
        notifier.settingsChanged.connect(self._settingsChanged)

    @staticmethod
    def _preferredEmojiFonts():
        return [
            "Emoji One",
            "Noto Color Emoji",
            "Noto Color Emoji [GOOG]",
            "Twitter Color Emoji",
            "OpenMoji Color",
            "Segoe UI Emoji",
            "Apple Color Emoji",
        ]

    def _findEmojiFont(self, fonts: List[str]):
        for font in self._preferredEmojiFonts():
            if font in fonts:
                return font

        return None

    def _setEmojiFont(self, family: str, size: int):
        self.setFont(QFont(family, size))
        self._hasEmojiFont = True

    def _setEmojiFontIfAvailable(self):
        if not self._settings.fonts.emojiEnabled:
            return

        allFonts = QFontDatabase().families()
        font = self._settings.fonts.emoji

        if font is not None:
            if font.family in allFonts:
                self._setEmojiFont(font.family, font.size)
                return

        fontFamily = self._findEmojiFont(allFonts)
        if fontFamily is not None:
            size = self._settings.fonts.standard.size
            self._setEmojiFont(fontFamily, size)

    def addCaptureMenu(self):
        name = "&Capture"
        if self._hasEmojiFont:
            if self._settings.fonts.emojiAddSpace:
                return self.addMenu(f"📱 {name}")
            else:
                return self.addMenu(f"📱{name}")
        else:
            return self.addMenu(name)

    def addToolsMenu(self):
        name = "&Tools"
        if self._hasEmojiFont:
            if self._settings.fonts.emojiAddSpace:
                return self.addMenu(f"🛠 {name}")
            else:
                return self.addMenu(f"🛠{name}")
        else:
            return self.addMenu(name)
