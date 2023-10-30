from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class ErrorDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Error")
        self.setIcon(QMessageBox.Critical)
        self.setStandardButtons(QMessageBox.Ok)
