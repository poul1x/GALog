from typing import Optional
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from galog.app.util.paths import styleSheetFile
from galog.app.util.style import CustomStyle

class LoadingDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setStyle(CustomStyle())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAccessibleName("LoadingDialog")
        self.initUserInterface()
        self.loadStyleSheet()

    def loadStyleSheet(self):
        with open(styleSheetFile("loading_dialog")) as f:
            self.setStyleSheet(f.read())

    def initUserInterface(self):
        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)

    def setText(self, text: str):
        self.label.setText(text)