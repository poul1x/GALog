from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget
from galog.app.ui.base.widget import BaseWidget

class BottomButtonBar(BaseWidget):
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
