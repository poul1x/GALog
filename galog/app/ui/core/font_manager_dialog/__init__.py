from typing import List

from galog.app.settings.models import FontSettings
from .font_manager_dialog import FontManagerDialog
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget


class StandardFontSelectionDialog(FontManagerDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent, "FontManagerDialog")
        self.setPreviewText("Lorem ipsum dolor sit amet")

    def _filterFonts(self, fonts: List[str]):
        return fonts

    def _writeFontSettings(self, fontSettings: FontSettings):
        self._settings.fonts.standard = fontSettings


class UpsizedFontSelectionDialog(FontManagerDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent, "FontManagerDialog")
        self.setPreviewText("Lorem ipsum dolor sit amet")

    def _filterFonts(self, fonts: List[str]):
        return fonts

    def _writeFontSettings(self, fontSettings: FontSettings):
        self._settings.fonts.upsized = fontSettings


class MonospacedFontSelectionDialog(FontManagerDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent, "FontManagerDialog")
        self.setPreviewText("App 'com.android.settings' is running")

    def _filterFonts(self, fonts: List[str]):
        return list(filter(self._monospaced, fonts))

    def _monospaced(self, fontFamily: str):
        return QFont(fontFamily).fixedPitch()

    def _writeFontSettings(self, fontSettings: FontSettings):
        self._settings.fonts.monospaced = fontSettings


class EmojiFontSelectionDialog(FontManagerDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent, "FontManagerDialog")
        self.setPreviewText("😂 ❤️ 🔥 🙏 😍 🤣")

    def _filterFonts(self, fonts: List[str]):
        return list(filter(self._emoji, fonts))

    def _emoji(self, fontFamily: str):
        return "emoji" in fontFamily.lower()

    def _writeFontSettings(self, fontSettings: FontSettings):
        self._settings.fonts.emoji = fontSettings


__all__ = [
    "StandardFontSelectionDialog",
    "UpsizedFontSelectionDialog",
    "MonospacedFontSelectionDialog",
    "EmojiFontSelectionDialog",
]
