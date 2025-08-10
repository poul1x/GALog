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


class LogViewerSettingsPane(Widget):
    liveReloadChanged = pyqtSignal(bool)
    textHighlightingChanged = pyqtSignal(bool)
    showLineNumbersChanged = pyqtSignal(bool)

    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(parent)
        self._settings = settings
        self._initUserInterface()
        self._initUserInputHandlers()

    def _initUserInputHandlers(self):
        self.liveReloadSection.valueChanged.connect(
            self.liveReloadChanged.emit,
        )
        self.textHighlightingSection.valueChanged.connect(
            self.textHighlightingChanged.emit
        )
        self.showLineNumbersSection.valueChanged.connect(
            self.showLineNumbersChanged.emit
        )

    def _initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)

        hBoxLayout = QHBoxLayout()
        self.titleLabel = QLabel(self)
        self.titleLabel.setText("Log viewer settings")
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

        self.liveReloadSection = ToggleSection(self._settings, self)
        self.liveReloadSection.setTitle("Live reload")
        liveReload = self._settings.logViewer.liveReload
        self.liveReloadSection.setValue(liveReload)

        self.textHighlightingSection = ToggleSection(self._settings, self)
        self.textHighlightingSection.setTitle("Text highlighting")
        textHighlighting = self._settings.logViewer.textHighlighting
        self.textHighlightingSection.setValue(textHighlighting)

        self.showLineNumbersSection = ToggleSection(self._settings, self)
        self.showLineNumbersSection.setTitle("Show line numbers")
        textHighlighting = self._settings.logViewer.textHighlighting
        self.showLineNumbersSection.setValue(textHighlighting)

        vBoxLayout.addWidget(self.liveReloadSection)
        vBoxLayout.addWidget(self.textHighlightingSection)
        vBoxLayout.addWidget(self.showLineNumbersSection)
        self.setLayout(vBoxLayout)

    def searchAdapters(self):
        return [
            self.liveReloadSection.searchAdapter(),
            self.textHighlightingSection.searchAdapter(),
            self.showLineNumbersSection.searchAdapter(),
        ]