from datetime import datetime
import os
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yaml
from loggat.app.components.capture_pane import CapturePane
from loggat.app.controllers.capture_pane import CapturePaneController
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
from loggat.app.util.paths import HIGHLIGHTING_RULES_FILE, STYLES_DIR

from ppadb.client import Client
from ppadb.device import Device


from .log_messages_pane import LogMessagesPane

ADB_HOST = "127.0.0.1"
ADB_PORT = 5037


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
    _liveReload: bool

    def __init__(self) -> None:
        super().__init__()
        self.loadStyleSheet()
        self.initUserInterface()
        self.initHighlighting()
        self._searchPane = None
        self._liveReload = True
        self.capturePaneController = CapturePaneController(ADB_HOST, ADB_PORT)

        # self.readSomeAndroidLogs()
        # self.lineRead(LogcatLine("W", "TAG", 12, "Visit https://aaa.ru"))
        # self.lineRead(LogcatLine("E", "TAG", "Buffer overflow 0xffffff"))



    def styleSheetFiles(self, path: str = STYLES_DIR):
        result = []
        for entry in os.scandir(path):
            if entry.is_file() and entry.path.endswith(".qss"):
                result.append(entry.path)
            elif entry.is_dir():
                result.extend(self.styleSheetFiles(entry.path))

        return result

    def loadStyleSheet(self):
        style = ""
        for filepath in self.styleSheetFiles():
            with open(filepath, "r", encoding="utf-8") as f:
                style += f.read() + "\n"

        self.setStyleSheet(style)

    def initHighlighting(self):
        self.highlightingRules = HighlightingRules()
        with open(HIGHLIGHTING_RULES_FILE) as f:
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

        if self._liveReload:
            centralWidget.pane.clear()
        # TODO: disable filter

        msg = f"App '{packageName}' started"
        centralWidget.pane.appendRow("S", "loggat", msg)

    def processStarted(self, event: ProcessStartedEvent):
        centralWidget: CentralWidget = self.centralWidget()
        msg = f"Process <PID={event.processId}> started for {event.target}"
        centralWidget.pane.appendRow("S", "loggat", msg)

    def processEnded(self, event: ProcessEndedEvent):
        centralWidget: CentralWidget = self.centralWidget()
        msg = f"Process <PID={event.processId}> ended"
        centralWidget.pane.appendRow("S", "loggat", msg)

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
        window.setLogMessage("qwerty efdfdfdasasa sasasasa https://google.com")
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

    def newCapture(self):
        capturePane = CapturePane(self)
        self.capturePaneController.setWidget(capturePane)
        self.capturePaneController.newCaptureDialog()

        if self.capturePaneController.captureTargetSelected():
            device = self.capturePaneController.getSelectedDevice()
            package = self.capturePaneController.getSelectedPackage()
            # self.logMessagesPaneController.startCapture(device, package)
            print(f"Start capture: {device} {package}")

    def actionStub(self):
        QMessageBox.information(self, "Stub", "Action stub")

    def newCaptureAction(self):
        action = QAction("&New", self)
        action.setShortcut("Ctrl+N")
        action.setStatusTip("Start new log capture")
        action.triggered.connect(lambda: self.newCapture())
        return action

    def startCaptureAction(self):
        action = QAction("&Start", self)
        # action.setShortcut("Ctrl+N")
        action.setStatusTip("Start log capture")
        action.triggered.connect(lambda: self.actionStub())
        return action

    def stopCaptureAction(self):
        action = QAction("&Stop", self)
        # action.setShortcut("Ctrl+N")
        action.setStatusTip("Stop log capture")
        action.triggered.connect(lambda: self.actionStub())
        return action

    def openLogFileAction(self):
        action = QAction("&Open", self)
        action.setShortcut("Ctrl+O")
        action.setStatusTip("Open log capture from file")
        action.triggered.connect(lambda: self.actionStub())
        return action

    def saveLogFileAction(self):
        action = QAction("&Save", self)
        action.setShortcut("Ctrl+S")
        action.setStatusTip("Save log capture to file")
        action.triggered.connect(lambda: self.actionStub())
        return action

    def installApkAction(self):
        action = QAction("&Install APK", self)
        action.setShortcut("Ctrl+I")
        action.setStatusTip("Install APK file")
        action.triggered.connect(lambda: self.actionStub())
        return action

    def setupMenuBar(self):
        menubar = self.menuBar()
        captureMenu = menubar.addMenu("&Capture")
        captureMenu.addAction(self.newCaptureAction())
        captureMenu.addAction(self.startCaptureAction())
        captureMenu.addAction(self.stopCaptureAction())
        captureMenu.addAction(self.openLogFileAction())
        captureMenu.addAction(self.saveLogFileAction())

        adbMenu = menubar.addMenu("&ADB")
        adbMenu.addAction(self.installApkAction())

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
