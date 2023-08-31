from datetime import datetime
from threading import Thread
from typing import Dict, List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from .log_messages_pane import LogMessagesPane



class CentralWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUserInterface()
        self.applyStyleSheets()

    def applyStyleSheets(self):

        file = QFile(":splitter.qss")
        if not file.open(QIODevice.ReadOnly):
            return

        self.setStyleSheet(file.readAll().data().decode())
        file.close()

    def initUserInterface(self):
        pane = LogMessagesPane(self)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(pane)
        self.setLayout(hBoxLayout)


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.initUserInterface()

    def setupExitAction(self):
        exitAction = QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAction)

    def setupQueueActions(self):

        # reloadAction = QAction("&Exit", self)
        # reloadAction.setShortcut("Ctrl+Q")
        # reloadAction.setStatusTip("Reload queue")
        # reloadAction.triggered.connect()

        queuePurgeAction = QAction("&Purge", self)
        # queuePurgeAction.setShortcut("Ctrl+Q")
        # queuePurgeAction.setStatusTip("Purge queue")

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&Queue")
        fileMenu.addAction(queuePurgeAction)

    def setupMenuBar(self):
        self.setupExitAction()

    def initUserInterface(self):

        self.resize(1900, 1200)
        self.setCentralWidget(CentralWidget())
        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("Loggat")
        self.setupMenuBar()
