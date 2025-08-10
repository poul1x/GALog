from typing import Callable
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal
from PyQt5.QtGui import QFocusEvent, QIcon, QRegExpValidator, QFont, QFontMetrics
from PyQt5.QtWidgets import (
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
from .section_search_adapter import SectionSearchAdapter
from galog.app.ui.core.font_manager_dialog import (
    EmojiFontSelectionDialog,
    MonospacedFontSelectionDialog,
    StandardFontSelectionDialog,
)


class ToggleSection(Widget):

    valueChanged = pyqtSignal(bool)

    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(parent)
        self._settings = settings
        self._initUserInterface()
        self._initUserInputHandlers()

    def _updateToggleButtonText(self):
        if self.toggleButton.isChecked():
            self.toggleButton.setText("ON")
        else:
            self.toggleButton.setText("OFF")

    def _toggleButtonClicked(self):
        self._updateToggleButtonText()
        self.valueChanged.emit(self.toggleButton.isChecked())

    def _initUserInputHandlers(self):
        self.toggleButton.clicked.connect(self._toggleButtonClicked)

    def _initUserInterface(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        alignLeft = Qt.AlignLeft | Qt.AlignVCenter
        alignRight = Qt.AlignRight | Qt.AlignVCenter

        self.titleLabel = QLabel(self)
        layout.addWidget(self.titleLabel, alignment=alignLeft)
        layout.addStretch()

        self.toggleButton = QPushButton(self)
        self.toggleButton.setCheckable(True)
        layout.addWidget(self.toggleButton, alignment=alignRight)
        self.setLayout(layout)

    def title(self):
        return self.titleLabel.text()

    def setTitle(self, title: str):
        self.titleLabel.setText(title)

    def value(self):
        return self.toggleButton.isChecked()

    def setValue(self, value: bool):
        self.toggleButton.setChecked(value)
        self._updateToggleButtonText()

    def searchAdapter(self):
        return ToggleSectionSearchAdapter(self)


class ToggleSectionSearchAdapter(SectionSearchAdapter):
    def __init__(self, section: ToggleSection):
        self._section = section

    def key(self):
        return self._section.title().lower()

    def value(self):
        return self._section

