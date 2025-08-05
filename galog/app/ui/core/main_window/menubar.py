import platform
from typing import List

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QMenuBar, QWidget
from galog.app.bootstrap import OS_NAME
from galog.app.settings import readSettings


class GALogMenuBar(QMenuBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._hasEmojiFont = False
        self._settings = readSettings()
        self._setEmojiFontIfAvailble()

    @staticmethod
    def _preferredEmojiFonts():
        if OS_NAME == "Windows":
            return ["Emoji One", "Segoe UI Emoji"]
        elif OS_NAME == "Linux":
            return ["Emoji One", "Noto Color Emoji", "Noto Color Emoji [GOOG]"]
        elif OS_NAME == "Darwin":
            return ["Emoji One", "Apple Color Emoji"]
        else:
            assert False, "Unreachable"

    def _findEmojiFont(self, fonts: List[str]):
        for font in self._preferredEmojiFonts():
            if font in fonts:
                return font

        return None

    def _setEmojiFont(self, family: str, size: int):
        emojiFont = QFont(family, size)
        self.setFont(emojiFont)
        self._hasEmojiFont = True

    def _setEmojiFontIfAvailble(self):
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
        if self._hasEmojiFont:
            return self.addMenu("📱 &Capture")
        else:
            return self.addMenu("&Capture")

    def addOptionsMenu(self):
        if self._hasEmojiFont:
            return self.addMenu("🛠 &Options")
        else:
            return self.addMenu("&Options")
