from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from galog.app.settings import AppSettings
from galog.app.ui.base.widget import Widget

from .font_settings_section import (
    LogViewerFontSection,
    MenuBarFontSection,
    StandardFontSection,
)
from .toggle_section import ToggleSection


class FontSettingsPane(Widget):
    standardFontChanged = pyqtSignal(str, int)
    logViewerFontChanged = pyqtSignal(str, int)
    menuBarFontChanged = pyqtSignal(str, int)
    emojiAddSpaceChanged = pyqtSignal(bool)
    emojiEnabledChanged = pyqtSignal(bool)

    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(parent)
        self._settings = settings
        self._initUserInterface()
        self._initUserInputHandlers()

    def _initUserInputHandlers(self):
        self.standardFontSection.fontChanged.connect(self.standardFontChanged.emit)
        self.logViewerFontSection.fontChanged.connect(self.logViewerFontChanged.emit)
        self.menuBarFontSection.fontChanged.connect(self.menuBarFontChanged.emit)
        self.emojiAddSpaceSection.valueChanged.connect(self.emojiAddSpaceChanged.emit)
        self.emojiEnabledSection.valueChanged.connect(self.emojiEnabledChanged.emit)

    def _initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)

        hBoxLayout = QHBoxLayout()
        self.titleLabel = QLabel(self)
        self.titleLabel.setText("Font settings")
        fontFamily = self._settings.fonts.standard.family
        fontSize = self._settings.fonts.standard.size - 1
        self.titleLabel.setFont(QFont(fontFamily, fontSize, QFont.Bold))

        self.lineFrame = QFrame(self)
        self.lineFrame.setFrameShape(QFrame.HLine)
        self.lineFrame.setFrameShadow(QFrame.Plain)
        self.lineFrame.setLineWidth(2)
        hBoxLayout.addWidget(self.titleLabel)
        hBoxLayout.addWidget(self.lineFrame, stretch=1)
        vBoxLayout.addLayout(hBoxLayout)

        self.standardFontSection = StandardFontSection(self._settings, self)
        self.logViewerFontSection = LogViewerFontSection(self._settings, self)
        self.menuBarFontSection = MenuBarFontSection(self._settings, self)

        self.emojiEnabledSection = ToggleSection(self._settings, self)
        self.emojiEnabledSection.setTitle("Use emoji symbols")
        self.emojiEnabledSection.setValue(self._settings.fonts.emojiEnabled)

        self.emojiAddSpaceSection = ToggleSection(self._settings, self)
        self.emojiAddSpaceSection.setTitle("Add space before emoji symbols")
        self.emojiAddSpaceSection.setValue(self._settings.fonts.emojiAddSpace)

        vBoxLayout.addWidget(self.standardFontSection)
        vBoxLayout.addWidget(self.logViewerFontSection)
        vBoxLayout.addWidget(self.menuBarFontSection)
        vBoxLayout.addWidget(self.emojiEnabledSection)
        vBoxLayout.addWidget(self.emojiAddSpaceSection)

        self.setLayout(vBoxLayout)

    def searchAdapters(self):
        return [
            self.standardFontSection.searchAdapter(),
            self.logViewerFontSection.searchAdapter(),
            self.menuBarFontSection.searchAdapter(),
            self.emojiEnabledSection.searchAdapter(),
            self.emojiAddSpaceSection.searchAdapter(),
        ]
