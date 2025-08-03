import platform

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QMenuBar, QWidget


class GALogMenuBar(QMenuBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._checkEmojiFontSupport()

    @staticmethod
    def _preferredEmojiFontFamily():
        system = platform.system()
        if system == "Windows":
            return "Segoe UI Emoji"
        elif system == "Linux":
            return "Emoji One"
        elif system == "Darwin":
            return "Apple Color Emoji"
        else:
            return None

    def _checkEmojiFontSupport(self):
        self._hasEmojiFont = False
        emojiFontFamily = self._preferredEmojiFontFamily()
        if emojiFontFamily in QFontDatabase().families():
            emojiFont = QFont(emojiFontFamily)
            self.setFont(emojiFont)
            self._hasEmojiFont = True

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
