from enum import Enum, auto

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget


class ButtonBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("BottomButtonBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.selectButton = QPushButton("Select")
        self.selectButton.setEnabled(False)
        self.selectButton.setProperty("name", "select")
        self.selectButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.selectButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setProperty("name", "cancel")
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.cancelButton)
        self.setLayout(layout)
