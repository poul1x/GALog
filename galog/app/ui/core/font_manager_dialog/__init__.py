from typing import List

from galog.app.settings.models import FontSettings
from galog.app.settings import AppSettings
from .font_manager_dialog import FontManagerDialog
from PyQt5.QtGui import QFont, QFontInfo
from PyQt5.QtWidgets import QWidget


class StandardFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent)
        self.setPreviewText("Lorem ipsum dolor sit amet")
        self.setTargetFontFamily(settings.fonts.standard.family)
        self.setTargetFontSize(settings.fonts.standard.size)


class LogViewerFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent)
        self.setPreviewText("App 'com.android.settings' is running")
        self.setTargetFontFamily(settings.fonts.logViewer.family)
        self.setTargetFontSize(settings.fonts.logViewer.size)

    def _filterFonts(self, fonts: List[str]):
        return list(filter(self._monospaced, fonts))

    def _monospaced(self, fontFamily: str):
        return QFontInfo(QFont(fontFamily)).fixedPitch()


class MenuBarFontSelectionDialog(FontManagerDialog):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent)
        self.setPreviewText("📱Capture 🛠Tools")
        menuBarFont = settings.fonts.menuBar
        self.setTargetFontFamily(menuBarFont.family)
        self.setTargetFontSize(menuBarFont.size)


__all__ = [
    "StandardFontSelectionDialog",
    "LogViewerFontSelectionDialog",
    "MenuBarFontSelectionDialog",
]
