from traceback import print_tb
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum


class Columns(int, Enum):
    logLevel = 0
    tagName = 1
    logMessage = 2


class LogMessageViewPane(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self._tagNameLabel = QLabel()
        self._logLevelLabel = QLabel()

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self._logLevelLabel)
        hBoxLayout.addWidget(self._tagNameLabel)

        self._logMessageText = QPlainTextEdit()
        self._logMessageText.setReadOnly(True)
        self._logMessageText.setReadOnly(True)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addWidget(self._logMessageText)

        self.setLayout(vBoxLayout)

        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def setTag(self, tag: str):
        self._tagNameLabel.setText(f"Tag: {tag}")

    def setLogLevel(self, level: str):
        self._logLevelLabel.setText(f"Log level: {level}")

    def setLogMessage(self, msg: str):
        self._logMessageText.setPlainText(msg)
