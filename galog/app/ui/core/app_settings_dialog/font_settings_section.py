from galog.app.settings import AppSettings
from .section_search_adapter import SectionSearchAdapter
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
from galog.app.ui.base.widget import Widget
from galog.app.ui.core.font_manager_dialog import (
    EmojiFontSelectionDialog,
    MonospacedFontSelectionDialog,
    StandardFontSelectionDialog,
    UpsizedFontSelectionDialog,
)


class StandardFontSection(Widget):

    fontChanged = pyqtSignal(str, int)

    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(parent)
        self._settings = settings
        self.setObjectClass("FontSettingsSection")
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initValue()

    def _fontChanged(self, fontFamily: str, fontSize: int):
        self.fontChanged.emit(fontFamily, fontSize)
        self.setValue(fontFamily, fontSize)

    def _fontSelectionDialog(self):
        return StandardFontSelectionDialog(self._settings, self)

    def _openFontSelectionDialog(self):
        dialog = self._fontSelectionDialog()
        dialog.fontSelected.connect(self._fontChanged)
        dialog.exec_()

    def _initValue(self):
        fontFamily = self._settings.fonts.standard.family
        fontSize = self._settings.fonts.standard.size
        self.setValue(fontFamily, fontSize)

    def _initUserInputHandlers(self):
        self.fontButton.clicked.connect(self._openFontSelectionDialog)

    def _initUserInterface(self):
        layout = QHBoxLayout()
        alignLeft = Qt.AlignLeft | Qt.AlignVCenter
        alignRight = Qt.AlignRight | Qt.AlignVCenter

        self.fontLabel = QLabel(self)
        self.fontLabel.setText("Standard font")
        layout.addWidget(self.fontLabel, alignment=alignLeft)
        layout.addStretch()

        self.fontButton = QPushButton(self)
        layout.addWidget(self.fontButton, alignment=alignRight)
        self.setLayout(layout)

    def title(self):
        return self.fontLabel.text()

    def setTitle(self, title: str):
        self.fontLabel.setText(title)

    def value(self):
        items = self.fontButton.text().split(" ")
        items[0], int(items[1]),

    def setValue(self, fontFamily: str, fontSize: int):
        self.fontButton.setText(f"{fontFamily} {fontSize}")

    def searchAdapter(self):
        return FontSectionSearchAdapter(self)


class FontSectionSearchAdapter(SectionSearchAdapter):
    def __init__(self, section: StandardFontSection):
        self._section = section

    def key(self):
        return self._section.title().lower()

    def value(self):
        return self._section


class UpsizedFontSection(StandardFontSection):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent)
        self.fontLabel.setText("Upsized font")

    def _fontSelectionDialog(self):
        return UpsizedFontSelectionDialog(self._settings, self)

    def _initValue(self):
        fontFamily = self._settings.fonts.upsized.family
        fontSize = self._settings.fonts.upsized.size
        self.setValue(fontFamily, fontSize)


class MonospacedFontSection(StandardFontSection):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent)
        self.fontLabel.setText("Monospaced font")

    def _fontSelectionDialog(self):
        return MonospacedFontSelectionDialog(self._settings, self)

    def _initValue(self):
        fontFamily = self._settings.fonts.monospaced.family
        fontSize = self._settings.fonts.monospaced.size
        self.setValue(fontFamily, fontSize)


class EmojiFontSection(StandardFontSection):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(settings, parent)
        self.fontLabel.setText("Emoji font")

    def _fontSelectionDialog(self):
        return EmojiFontSelectionDialog(self._settings, self)

    def _initValue(self):
        fontFamily = self._settings.fonts.emoji.family
        fontSize = self._settings.fonts.emoji.size
        self.setValue(fontFamily, fontSize)
