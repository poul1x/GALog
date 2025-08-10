from typing import List

from galog.app.settings.models import FontSettings
from galog.app.settings import AppSettings
from .font_manager_dialog import FontManagerDialog
from PyQt5.QtGui import QFont, QFontInfo
from PyQt5.QtWidgets import QWidget


class StandardFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent, "FontManagerDialog")
        self.setPreviewText("Lorem ipsum dolor sit amet")
        self.setTargetFontFamily(settings.fonts.standard.family)
        self.setTargetFontSize(settings.fonts.standard.size)

class UpsizedFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent, "FontManagerDialog")
        self.setPreviewText("Lorem ipsum dolor sit amet")
        self.setTargetFontFamily(settings.fonts.upsized.family)
        self.setTargetFontSize(settings.fonts.upsized.size)


class MonospacedFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent, "FontManagerDialog")
        self.setPreviewText("App 'com.android.settings' is running")
        self.setTargetFontFamily(settings.fonts.monospaced.family)
        self.setTargetFontSize(settings.fonts.monospaced.size)

    def _filterFonts(self, fonts: List[str]):
        return list(filter(self._monospaced, fonts))

    def _monospaced(self, fontFamily: str):
        return QFontInfo(QFont(fontFamily)).fixedPitch()


class EmojiFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent, "FontManagerDialog")
        self.setPreviewText("😂 ❤️ 🔥 🙏 😍 🤣")
        self.setTargetFontFamily(settings.fonts.emoji.family)
        self.setTargetFontSize(settings.fonts.emoji.size)

    def _filterFonts(self, fonts: List[str]):
        return list(filter(self._emoji, fonts))

    def _emoji(self, fontFamily: str):
        return "emoji" in fontFamily.lower()


__all__ = [
    "StandardFontSelectionDialog",
    "UpsizedFontSelectionDialog",
    "MonospacedFontSelectionDialog",
    "EmojiFontSelectionDialog",
]
