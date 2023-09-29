from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yaml
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane

from loggat.app.logcat import (
    AndroidAppLogReader,
    AndroidLogReader,
    LogcatLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)
from loggat.app.mtsearch import SearchItem, SearchItemTask, SearchResult


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
        self.pane = LogMessagesPane(self)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self.pane)
        self.setLayout(hBoxLayout)


class MainWindow(QMainWindow):
    _logReader: Optional[AndroidLogReader]
    _viewWindows: List[LogMessageViewPane]

    def __init__(self) -> None:
        super().__init__()
        self.initUserInterface()
        self.initHighlighting()
        self._searchPane = None

        self.readSomeAndroidLogs()
        # self.lineRead(LogcatLine("E", "TAG", "Visit https://aaa.ru"))
        # self.lineRead(LogcatLine("E", "TAG", "Buffer overflow 0xffffff"))
        self.n = 0

    def initHighlighting(self):
        self.highlightingRules = HighlightingRules()
        with open("config/highlighting_rules.yaml") as f:
            rules = yaml.load_all(f, yaml.SafeLoader)
            self.highlightingRules.load(rules)

        pane = self.centralWidget().pane
        pane.setHighlightingRules(self.highlightingRules)

    def lineRead(self, parsedLine: LogcatLine):
        centralWidget: CentralWidget = self.centralWidget()
        centralWidget.pane.appendRow(
            parsedLine.level,
            parsedLine.tag,
            parsedLine.msg,
        )

    def appStarted(self, packageName: str):
        centralWidget: CentralWidget = self.centralWidget()
        msg = f"App '{packageName}' started"
        centralWidget.pane.appendRow("S", "loggat", msg)

    def processStarted(self, event: ProcessStartedEvent):
        centralWidget: CentralWidget = self.centralWidget()
        msg = "New process <PID=%s, APP='%s'> started for %s"
        args = event.processId, event.packageName, event.target
        centralWidget.pane.appendRow("S", "loggat", msg % args)

    def processEnded(self, event: ProcessEndedEvent):
        centralWidget: CentralWidget = self.centralWidget()
        msg = "Process <PID=%s, APP='%s'> ended"
        args = event.processId, event.packageName
        centralWidget.pane.appendRow("S", "loggat", msg % args)

    def appEnded(self, packageName: str):
        centralWidget: CentralWidget = self.centralWidget()
        msg = f"App '{packageName}' ended"
        centralWidget.pane.appendRow("S", "loggat", msg)

    def centralWidget(self) -> CentralWidget:
        return super().centralWidget()

    def showSearchPane(self):
        self.centralWidget().pane.enableDisableFilter()

    def openLogMessageViewPane(self):
        window = LogMessageViewPane(self)
        window.setTag("Portswertive")
        window.setLogLevel("I")
        window.setLogMessage("qwerty efdfdfdasasa sasasasa")
        window.exec_()

    def readSomeAndroidLogs(self):
        self.startReadingAndroidLog()
        # sleep(0.5)
        # self.stopReadingAndroidLog()

    def startReadingAndroidLog(self):
        self._logReader = AndroidAppLogReader(
            "127.0.0.1", 5037, "15151JEC210855", "org.telegram.messenger"
        )
        self._logReader.signals.appStarted.connect(self.appStarted)
        self._logReader.signals.processStarted.connect(self.processStarted)
        self._logReader.signals.processEnded.connect(self.processEnded)
        self._logReader.signals.appEnded.connect(self.appEnded)
        self._logReader.signals.lineRead.connect(self.lineRead)
        self._logReader.start()

    def stopReadingAndroidLog(self):
        self._logReader.stop()
        # self._logReader = None

    def closeEvent(self, event: QEvent):
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
        exitAction.triggered.connect(lambda: self.close())

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

    def setupViewAction(self):
        action = QAction("&View", self)
        action.setShortcut("Ctrl+W")
        action.setStatusTip("View")
        action.triggered.connect(self.openLogMessageViewPane)

        menubar = self.menuBar()
        menu = menubar.addMenu("&Qwerty")
        menu.addAction(action)

    def setupMenuBar(self):
        self.setupExitAction()
        self.setupSearchAction()
        self.setupViewAction()

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
