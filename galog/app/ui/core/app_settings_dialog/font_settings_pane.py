from typing import Callable
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal
from PyQt5.QtGui import QFocusEvent, QIcon, QRegExpValidator, QFont, QFontMetrics
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QSpinBox,
    QTextEdit,
)

from galog.app.paths import iconFile
from galog.app.settings.constants import MAX_FONT_SIZE, MIN_FONT_SIZE
from galog.app.settings import readSettings
from galog.app.settings import AppSettings
from galog.app.ui.base.widget import Widget
from .toggle_section import ToggleSection

from .font_settings_section import (
    StandardFontSection,
    MonospacedFontSection,
    EmojiFontSection,
    UpsizedFontSection,
)


class FontSettingsPane(Widget):
    standardFontChanged = pyqtSignal(str, int)
    upsizedFontChanged = pyqtSignal(str, int)
    monospacedFontChanged = pyqtSignal(str, int)
    emojiFontChanged = pyqtSignal(str, int)
    emojiAddSpaceChanged = pyqtSignal(bool)
    emojiEnabledChanged = pyqtSignal(bool)

    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(parent)
        self._settings = settings
        self._initUserInterface()
        self._initUserInputHandlers()

    def _initUserInputHandlers(self):
        self.standardFontSection.fontChanged.connect(self.standardFontChanged.emit)
        self.upsizedFontSection.fontChanged.connect(self.upsizedFontChanged.emit)
        self.monospacedFontSection.fontChanged.connect(self.monospacedFontChanged.emit)
        self.emojiFontSection.fontChanged.connect(self.emojiFontChanged.emit)
        self.emojiAddSpaceSection.valueChanged.connect(self.emojiAddSpaceChanged.emit)
        self.emojiEnabledSection.valueChanged.connect(self.emojiEnabledChanged.emit)

    def _initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        self.standardFontSection = StandardFontSection(self._settings, self)
        self.upsizedFontSection = UpsizedFontSection(self._settings, self)
        self.monospacedFontSection = MonospacedFontSection(self._settings, self)
        self.emojiFontSection = EmojiFontSection(self._settings, self)

        self.emojiEnabledSection = ToggleSection(self._settings, self)
        self.emojiEnabledSection.setTitle("Use emoji symbols")
        self.emojiEnabledSection.setValue(self._settings.fonts.emoji.enabled)

        self.emojiAddSpaceSection = ToggleSection(self._settings, self)
        self.emojiAddSpaceSection.setTitle("Add space before emoji symbols")
        self.emojiAddSpaceSection.setValue(self._settings.fonts.emoji.addSpace)

        self.e1mojiAddSpaceSection = ToggleSection(self._settings, self)
        self.e1mojiAddSpaceSection.setTitle("Add space before emoji symbols")
        self.e1mojiAddSpaceSection.setValue(self._settings.fonts.emoji.addSpace)

        self.e2mojiAddSpaceSection = ToggleSection(self._settings, self)
        self.e2mojiAddSpaceSection.setTitle("Add space before emoji symbols")
        self.e2mojiAddSpaceSection.setValue(self._settings.fonts.emoji.addSpace)

        vBoxLayout.addWidget(self.standardFontSection)
        vBoxLayout.addWidget(self.upsizedFontSection)
        vBoxLayout.addWidget(self.monospacedFontSection)
        vBoxLayout.addWidget(self.emojiFontSection)
        vBoxLayout.addWidget(self.emojiEnabledSection)
        vBoxLayout.addWidget(self.emojiAddSpaceSection)
        vBoxLayout.addWidget(self.e1mojiAddSpaceSection)
        vBoxLayout.addWidget(self.e2mojiAddSpaceSection)

        self.setLayout(vBoxLayout)

    def searchAdapters(self):
        return [
            self.standardFontSection.searchAdapter(),
            self.upsizedFontSection.searchAdapter(),
            self.monospacedFontSection.searchAdapter(),
            self.emojiFontSection.searchAdapter(),
            self.emojiEnabledSection.searchAdapter(),
            self.emojiAddSpaceSection.searchAdapter(),
        ]
