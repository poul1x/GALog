from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class BottomButtonBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        self.buttonSave = QPushButton("Save", self)
        self.buttonCancel = QPushButton("Cancel", self)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setAlignment(Qt.AlignRight)
        hBoxLayout.addWidget(self.buttonSave)
        hBoxLayout.addWidget(self.buttonCancel)
        self.setLayout(hBoxLayout)
