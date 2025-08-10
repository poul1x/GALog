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
    QSizePolicy,
    QFrame,
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
        self._setFixedSizePolicy()

    def _initUserInputHandlers(self):
        self.standardFontSection.fontChanged.connect(self.standardFontChanged.emit)
        self.upsizedFontSection.fontChanged.connect(self.upsizedFontChanged.emit)
        self.monospacedFontSection.fontChanged.connect(self.monospacedFontChanged.emit)
        self.emojiFontSection.fontChanged.connect(self.emojiFontChanged.emit)
        self.emojiAddSpaceSection.valueChanged.connect(self.emojiAddSpaceChanged.emit)
        self.emojiEnabledSection.valueChanged.connect(self.emojiEnabledChanged.emit)

    def _initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)

        hBoxLayout = QHBoxLayout()
        self.titleLabel = QLabel(self)
        self.titleLabel.setText("Font settings")
        fontFamily = self._settings.fonts.upsized.family
        fontSize = self._settings.fonts.upsized.size
        self.titleLabel.setFont(QFont(fontFamily, fontSize, QFont.Bold))

        self.lineFrame = QFrame(self)
        self.lineFrame.setFrameShape(QFrame.HLine)
        self.lineFrame.setFrameShadow(QFrame.Plain)
        self.lineFrame.setLineWidth(2)
        hBoxLayout.addWidget(self.titleLabel)
        hBoxLayout.addWidget(self.lineFrame, stretch=1)
        vBoxLayout.addLayout(hBoxLayout)

        self.standardFontSection = StandardFontSection(self._settings, self)
        self.upsizedFontSection = UpsizedFontSection(self._settings, self)
        self.monospacedFontSection = MonospacedFontSection(self._settings, self)
        self.emojiFontSection = EmojiFontSection(self._settings, self)

        self.emojiEnabledSection = ToggleSection(self._settings, self)
        self.emojiEnabledSection.setTitle("Use emoji symbols")
        self.emojiEnabledSection.setValue(self._settings.fonts.emojiEnabled)

        self.emojiAddSpaceSection = ToggleSection(self._settings, self)
        self.emojiAddSpaceSection.setTitle("Add space before emoji symbols")
        self.emojiAddSpaceSection.setValue(self._settings.fonts.emojiAddSpace)

        vBoxLayout.addWidget(self.standardFontSection)
        vBoxLayout.addWidget(self.upsizedFontSection)
        vBoxLayout.addWidget(self.monospacedFontSection)
        vBoxLayout.addWidget(self.emojiFontSection)
        vBoxLayout.addWidget(self.emojiEnabledSection)
        vBoxLayout.addWidget(self.emojiAddSpaceSection)

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

    def _setFixedSizePolicy(self):
        for widget in self.findChildren(QWidget):
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
