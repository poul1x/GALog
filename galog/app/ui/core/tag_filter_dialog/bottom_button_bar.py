from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget

from galog.app.ui.base.widget import Widget


class BottomButtonBar(Widget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        self.buttonSave = QPushButton("Save", self)
        self.buttonSave.setProperty("name", "save")
        self.buttonCancel = QPushButton("Cancel", self)
        self.buttonCancel.setProperty("name", "cancel")
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setAlignment(Qt.AlignRight)
        hBoxLayout.addWidget(self.buttonSave)
        hBoxLayout.addWidget(self.buttonCancel)
        self.setLayout(hBoxLayout)
