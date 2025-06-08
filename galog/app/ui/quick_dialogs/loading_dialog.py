from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from galog.app.ui.base.dialog import Dialog
from galog.app.ui.base.widget import Widget


class LoadingDialog(Dialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUserInterface()
        self.setMinimumWidth(350)
        self.adjustSize()
        self.moveToCenter()

    def initUserInterface(self):
        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)

        container = Widget(self)
        container.setObjectName("Container")
        container.setLayout(layout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(container)
        self.setLayout(mainLayout)

    def setText(self, text: str):
        self.label.setText(text)
