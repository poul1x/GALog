from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QFocusEvent, QIcon, QRegExpValidator, QFont
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
from galog.app.ui.base.widget import Widget


class FontPreviewPane(Widget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()
        alignLeft = Qt.AlignLeft | Qt.AlignVCenter
        alignRight = Qt.AlignRight | Qt.AlignVCenter


        self.fontPreview = QLabel(self)
        self.fontPreview.setWordWrap(False)
        layout.addWidget(self.fontPreview, alignment=alignLeft)
        layout.addStretch()

        self.fontSizeSpinBox = QSpinBox(self)
        self.fontSizeSpinBox.setReadOnly(False)
        self.fontSizeSpinBox.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.fontSizeSpinBox.setSingleStep(1)
        layout.addWidget(self.fontSizeSpinBox, alignment=alignRight)
        self.setLayout(layout)

    def _updateFontPreview(self):
        font = QFont(self.fontFamily(), self.fontSize())
        self.fontPreview.setFont(font)

    def fontFamily(self):
        return self.fontPreview.text()

    def setFontFamily(self, fontFamily: str):
        self.fontPreview.setText(fontFamily)
        self._updateFontPreview()

    def fontSize(self):
        return self.fontSizeSpinBox.value()

    def setFontSize(self, fontSize: int):
        self.fontSizeSpinBox.setValue(fontSize)
        self._updateFontPreview()

    def setPreviewText(self):
        pass