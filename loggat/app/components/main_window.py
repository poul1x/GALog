from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from loggat.app.logcat import (
    AndroidLogReader,
    LogcatLine,
)


from .log_messages_pane import LogMessagesPane
from .search_pane import SearchPane


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
        self.pane = LogMessagesPane(self)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self.pane)
        self.setLayout(hBoxLayout)



class MainWindow(QMainWindow):
    _logReader: Optional[AndroidLogReader]
    _searchPane: Optional[SearchPane]

    def __init__(self) -> None:
        super().__init__()
        self.initUserInterface()
        self.readSomeAndroidLogs()
        self._searchPane = None

    def lineRead(self, parsedLine: LogcatLine):
        centralWidget: CentralWidget = self.centralWidget()
        centralWidget.pane.appendRow(
            parsedLine.level,
            parsedLine.tag,
            parsedLine.msg,
        )

    def centralWidget(self) -> CentralWidget:
        return super().centralWidget()

    def showSearchPane(self):
        if self._searchPane:
            self._searchPane.activateWindow()
            self._searchPane.raise_()
        else:
            self._searchPane = SearchPane(self.centralWidget().pane, None)
            self._searchPane.show()

    def readSomeAndroidLogs(self):
        self.startReadingAndroidLog()
        sleep(0.5)
        self.stopReadingAndroidLog()

    def startReadingAndroidLog(self):
        self._logReader = AndroidLogReader("127.0.0.1", 5037, "15151JEC210855")
        self._logReader.lineRead.connect(self.lineRead)
        self._logReader.start()

    def stopReadingAndroidLog(self):
        self._logReader.stop()
        # self._logReader = None

    def quitSafe(self):
        self.stopReadingAndroidLog()
        qApp.quit()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to close the window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.stopReadingAndroidLog()
            event.accept()
        else:
            event.ignore()

    def setupExitAction(self):
        exitAction = QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(self.quitSafe)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAction)

    def setupSearchAction(self):
        action = QAction("&Search", self)
        action.setShortcut("Ctrl+F")
        action.setStatusTip("Search")
        action.triggered.connect(self.showSearchPane)

        menubar = self.menuBar()
        menu = menubar.addMenu("&Messages")
        menu.addAction(action)

    def setupMenuBar(self):
        self.setupExitAction()
        self.setupSearchAction()

    def initUserInterface(self):

        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        self.setCentralWidget(CentralWidget())
        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("Loggat")
        self.setupMenuBar()
