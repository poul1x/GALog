from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout


class BottomButtonBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        buttonSave = QPushButton("Save", self)
        buttonCancel = QPushButton("Cancel", self)
        hBoxLayout.setContentsMargins(0,0,0,0)
        hBoxLayout.setAlignment(Qt.AlignRight)
        hBoxLayout.addWidget(buttonSave)
        hBoxLayout.addWidget(buttonCancel)
        self.setLayout(hBoxLayout)
