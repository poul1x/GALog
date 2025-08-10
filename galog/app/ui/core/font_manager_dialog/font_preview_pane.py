from typing import Callable
from PyQt5.QtCore import QRegExp, Qt
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
from galog.app.ui.base.widget import Widget


class FontPreviewPane(Widget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._initUserInterface()
        self._initUserInputHandlers()
        self.setPreviewText("Preview text")

    def _initUserInputHandlers(self):
        self.fontSizeSpinBox.valueChanged.connect(self._fontSizeChanged)

    def _initUserInterface(self):
        layout = QHBoxLayout()
        alignLeft = Qt.AlignLeft | Qt.AlignVCenter
        alignRight = Qt.AlignRight | Qt.AlignVCenter

        self.fontPreviewLabel = QLabel(self)
        self.fontPreviewLabel.setWordWrap(False)
        layout.addWidget(self.fontPreviewLabel, alignment=alignLeft)
        layout.addStretch()

        self.fontSizeSpinBox = QSpinBox(self)
        self.fontSizeSpinBox.setSingleStep(1)
        self.fontSizeSpinBox.setReadOnly(False)
        self.fontSizeSpinBox.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.fontSizeSpinBox.setValue(self.fontPreviewLabel.font().pointSize())
        self._fontSizeChanged(self.fontSizeSpinBox.value()) # need this

        layout.addWidget(self.fontSizeSpinBox, alignment=alignRight)
        self.setLayout(layout)

    def _fontSizeChanged(self, value: int):
        font = QFont(self.targetFontFamily(), value)
        self.fontPreviewLabel.setFont(font)

        height = QFontMetrics(font).height()
        self.fontPreviewLabel.setFixedHeight(height)

    def targetFontFamily(self):
        return self.fontPreviewLabel.font().family()

    def targetFontSize(self):
        return self.fontPreviewLabel.font().pointSize()

    def setTargetFontFamily(self, fontFamily: str):
        font = QFont(fontFamily, self.targetFontSize())
        self.fontPreviewLabel.setFont(font)

    def setTargetFontSize(self, size: int):
        font = QFont(self.targetFontFamily(), size)
        self.fontPreviewLabel.setFont(font)

    def setPreviewText(self, text: str):
        self.fontPreviewLabel.setText(text)
