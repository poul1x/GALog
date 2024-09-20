from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class MessageBoxButtonBar(QWidget):
    buttonClicked = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName("MessageBoxButtonBar")
        self.initUserInterface()
        self._buttonCount = 0

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout(self)
        hBoxLayout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setSpacing(0)
        self.setLayout(hBoxLayout)

    def addButton(self, name: str):
        buttonId = self._buttonCount
        button = QPushButton(name, self)
        button.clicked.connect(lambda: self.buttonClicked.emit(buttonId))
        self.layout().addWidget(button)
        self._buttonCount += 1
        return buttonId

    def setDefaultButton(self, buttonId: int):
        layout = self.layout()
        assert buttonId >= 0
        assert buttonId < layout.count()

        button = self.layout().itemAt(buttonId).widget()
        assert isinstance(button, QPushButton)
        button.setDefault(True)

    def buttonCount(self):
        return self._buttonCount
