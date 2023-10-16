from datetime import datetime
import os
from queue import Queue
import shutil
import subprocess
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yaml
from loggat.app.components.capture_pane import CapturePane
from loggat.app.controllers.capture_pane.capture_pane import CapturePaneController
from loggat.app.controllers.log_messages_pane.controller import LogMessagesPaneController
from loggat.app.controllers.log_messages_pane.log_reader import AndroidAppLogReader, LogLine, ProcessEndedEvent, ProcessStartedEvent
from loggat.app.device.device import AdbClient
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane
from loggat.app.util.style import CustomStyle

from loggat.app.util.paths import HIGHLIGHTING_RULES_FILE, STYLES_DIR

from .. import app_strings

from .log_messages_pane import LogMessagesPane

ADB_HOST = "127.0.0.1"
ADB_PORT = 5037


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        self.logMessagesPane = LogMessagesPane(self)
        hBoxLayout.addWidget(self.logMessagesPane)
        self.setLayout(hBoxLayout)


class MainWindow(QMainWindow):
    _viewWindows: List[LogMessageViewPane]
    _liveReload: bool

    def __init__(self) -> None:
        super().__init__()
        self._searchPane = None
        self._liveReload = True
        self.capturePaneController = CapturePaneController(ADB_HOST, ADB_PORT)
        self.logMessagesPaneController = LogMessagesPaneController(ADB_HOST, ADB_PORT)
        self.loadAppStrings()
        self.loadStyleSheet()
        self.initHighlighting()
        self.initUserInterface()
        self.setStyle(CustomStyle())


    def loadAppStrings(self):
        app_strings.init("en")

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
        rules = HighlightingRules()
        with open(HIGHLIGHTING_RULES_FILE) as f:
            content = yaml.load_all(f, yaml.SafeLoader)
            rules.load(content)

        self.logMessagesPaneController.setHighlightingRules(rules)

    def centralWidget(self) -> CentralWidget:
        return super().centralWidget()


    def closeEvent(self, event: QEvent):
        reply = QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to close the window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.logMessagesPaneController.stopCapture()
            event.accept()
        else:
            event.ignore()

    def newCapture(self):
        capturePane = CapturePane(self)
        self.capturePaneController.setWidget(capturePane)
        self.capturePaneController.newCaptureDialog()

        if self.capturePaneController.captureTargetSelected():
            device = self.capturePaneController.selectedDevice()
            package = self.capturePaneController.selectedPackage()
            self.logMessagesPaneController.startCapture(device, package)

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

        centralWidget = CentralWidget()
        self.logMessagesPaneController.takeControl(centralWidget.logMessagesPane)
        self.setCentralWidget(centralWidget)
        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("Loggat")
        self.setupMenuBar()
