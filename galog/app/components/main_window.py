from contextlib import suppress
from datetime import datetime
import os
from queue import Queue
import shutil
import subprocess
import sys
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
import yaml
from galog.app.components.capture_pane import CapturePane, RunAppAction
from galog.app.components.dialogs.stop_capture_dialog import (
    StopCaptureDialog,
    StopCaptureDialogResult,
)
from galog.app.controllers.capture_pane import CapturePaneController
from galog.app.controllers.install_app import InstallAppController
from galog.app.controllers.kill_app import KillAppController
from galog.app.controllers.log_messages_pane.controller import (
    LogMessagesPaneController,
)
from galog.app.controllers.log_messages_pane.log_reader import (
    AndroidAppLogReader,
    LogLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)
from galog.app.controllers.run_app.controller import RunAppController
from galog.app.device.device import AdbClient
from galog.app.highlighting_rules import HighlightingRules
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.util.messagebox import showErrorMsgBox, showNotImpMsgBox, showQuitMsgBox
from galog.app.util.style import CustomStyle

from galog.app.util.paths import (
    FONTS_DIR,
    HIGHLIGHTING_RULES_FILE,
    STYLES_DIR,
    iconFile,
)

from .. import app_strings

from .log_messages_pane import LogMessagesPane

ADB_HOST = "127.0.0.1"
ADB_PORT = 5037


class MainWindow(QMainWindow):
    _viewWindows: List[LogMessageViewPane]
    _liveReload: bool

    def __init__(self) -> None:
        super().__init__()
        self._searchPane = None
        self._liveReload = True
        self.capturePaneController = CapturePaneController(ADB_HOST, ADB_PORT)
        self.logMessagesPaneController = LogMessagesPaneController(ADB_HOST, ADB_PORT)
        self.startAdbServer()
        self.loadAppStrings()
        self.loadStyleSheet()
        self.loadFonts()
        self.initHighlighting()
        self.initUserInterface()
        self.setStyle(CustomStyle())

    def startAdbServer(self):
        adb = shutil.which("adb")
        if not adb:
            return

        def execAdbServer():
            with suppress(subprocess.SubprocessError):
                subprocess.call(
                    args=[adb, "server"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )

        QThreadPool.globalInstance().start(execAdbServer)

    def loadAppStrings(self):
        app_strings.init("en")

    def fontFiles(self, path: str = FONTS_DIR):
        result = []
        for entry in os.scandir(path):
            if entry.is_file() and entry.path.endswith(".ttf"):
                result.append(entry.path)
            elif entry.is_dir():
                result.extend(self.styleSheetFiles(entry.path))

        return result

    def styleSheetFiles(self, path: str = STYLES_DIR):
        result = []
        for entry in os.scandir(path):
            if entry.is_file() and entry.path.endswith(".qss"):
                result.append(entry.path)
            elif entry.is_dir():
                result.extend(self.styleSheetFiles(entry.path))

        return result

    def loadFonts(self):
        fontDB = QFontDatabase()
        for filepath in self.fontFiles():
            fontDB.addApplicationFont(filepath)

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

    def closeEvent(self, event: QEvent):
        if showQuitMsgBox():
            self.logMessagesPaneController.stopCapture()
            event.accept()
        else:
            event.ignore()

    def _iterateActions(self):
        menuBar = self.menuBar()
        for fileMenu in menuBar.findChildren(QMenu):
            for action in fileMenu.actions():
                yield action

    def _iterateWidgetActions(self):
        for action in self._iterateActions():
            if isinstance(action, QWidgetAction):
                yield action

    def _iterateCheckableWidgetActions(self):
        for action in self._iterateWidgetActions():
            if isinstance(action.defaultWidget(), QCheckBox):
                yield action

    def setCaptureSpecificActionsEnabled(self, enabled: bool):
        menuBar = self.menuBar()
        for fileMenu in menuBar.findChildren(QMenu):
            for action in fileMenu.actions():
                if action.data() == True:
                    action.setEnabled(enabled)

    def increaseHoverAreaForCheckableActions(self):
        #
        # This is a workaround to increase hover area
        # around checkbox placed inside QWidgetAction.
        # The idea is to pad the right part of the checkbox text
        # with spaces which leads to hover area expansion
        #

        maxLength = 15 # Approximate menu item text max length in spaces
        for action in self._iterateCheckableWidgetActions():
            checkBox: QCheckBox = action.defaultWidget()
            textLength = len(checkBox.text())
            if textLength > maxLength:
                maxLength = textLength

        addSpacesDefault = 2 # even
        for action in self._iterateCheckableWidgetActions():
            checkBox: QCheckBox = action.defaultWidget()
            addSpaces = addSpacesDefault + 2 * (maxLength - len(checkBox.text()))
            checkBox.setText(checkBox.text() + " " * addSpaces)

    def startCapture(self):
        capturePane = CapturePane(self)
        self.capturePaneController.takeControl(capturePane)
        self.capturePaneController.startCaptureDialog()

        if self.capturePaneController.captureTargetSelected():
            device = self.capturePaneController.selectedDevice()
            package = self.capturePaneController.selectedPackage()
            action = self.capturePaneController.selectedAction()

            if action != RunAppAction.DoNotStartApp:
                controller = RunAppController(ADB_HOST, ADB_PORT)
                controller.setAppDebug(action == RunAppAction.StartAppDebug)
                controller.runApp(device, package)

            self.logMessagesPaneController.startCapture(device, package)
            self.setCaptureSpecificActionsEnabled(True)

    def stopCapture(self):
        dialog = StopCaptureDialog()
        result = dialog.exec_()
        if result == StopCaptureDialogResult.Rejected:
            return

        if result == StopCaptureDialogResult.AcceptedKillApp:
            device = self.logMessagesPaneController.device
            package = self.logMessagesPaneController.package
            controller = KillAppController(ADB_HOST, ADB_PORT)
            controller.killApp(device, package)

        self.logMessagesPaneController.stopCapture()
        self.setCaptureSpecificActionsEnabled(False)

    def enableMessageFilter(self):
        self.logMessagesPaneController.enableMessageFilter()

    def toggleLiveReload(self, checkBox: QCheckBox):
        self.logMessagesPaneController.setLiveReloadEnabled(checkBox.isChecked())

    def toggleShowLineNumbers(self, checkBox: QCheckBox):
        self.logMessagesPaneController.setShowLineNumbers(checkBox.isChecked())

    def handleInstallApkAction(self):
        device = self.capturePaneController.selectedDevice()
        if device is None:
            msgBrief = "Operation failed"
            msgVerbose = "No device selected (Select device in 'Capture->New' [tmp])"
            showErrorMsgBox(msgBrief, msgVerbose)
            return

        controller = InstallAppController(ADB_HOST, ADB_PORT)
        controller.promptInstallApp(device)

    def startCaptureAction(self):
        action = QAction("&New", self)
        action.setShortcut("Ctrl+N")
        action.setStatusTip("Start new log capture")
        action.triggered.connect(lambda: self.startCapture())
        action.setEnabled(True)
        action.setData(False)
        return action

    def messageFilterAction(self):
        action = QAction("&Find", self)
        action.setShortcut("Ctrl+F")
        action.setStatusTip("Toggle message filter mode")
        action.triggered.connect(lambda: self.enableMessageFilter())
        action.setEnabled(True)
        action.setData(False)
        return action

    def stopCaptureAction(self):
        action = QAction("&Stop", self)
        action.setShortcut("Ctrl+Q")
        action.setStatusTip("Stop capture")
        action.triggered.connect(lambda: self.stopCapture())
        action.setEnabled(False)
        action.setData(True)
        return action

    def openLogFileAction(self):
        action = QAction("&Open", self)
        action.setShortcut("Ctrl+O")
        action.setStatusTip("Open log capture from file")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(True)
        action.setData(False)
        return action

    def saveLogFileAction(self):
        action = QAction("&Save", self)
        action.setShortcut("Ctrl+S")
        action.setStatusTip("Save log capture to file")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action

    def liveReloadAction(self):
        action = QWidgetAction(self)
        checkBox = QCheckBox("Live reload")
        checkBox.setChecked(True)
        checkBox.stateChanged.connect(lambda: self.toggleLiveReload(checkBox))
        action.setDefaultWidget(checkBox)
        action.setStatusTip("Enable/disable log pane reload on app restart")
        action.setEnabled(True)
        action.setData(False)
        return action

    def showLineNumbersAction(self):
        action = QWidgetAction(self)
        checkBox = QCheckBox("Show line numbers")
        checkBox.setChecked(False)
        checkBox.stateChanged.connect(lambda: self.toggleShowLineNumbers(checkBox))
        action.setDefaultWidget(checkBox)
        action.setStatusTip("Show/Hide log line numbers")
        action.setEnabled(True)
        action.setData(False)
        return action

    def installApkAction(self):
        action = QAction("&Install APK", self)
        action.setShortcut("Ctrl+I")
        action.setStatusTip("Install app from APK file")
        action.triggered.connect(self.handleInstallApkAction)
        action.setEnabled(True)
        action.setData(False)
        return action

    def clearAppDataAction(self):
        action = QAction("&Clear app data", self)
        action.setShortcut("Ctrl+P")
        action.setStatusTip("Clear user data associated with the app")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action

    def takeScreenshotAction(self):
        action = QAction("&Take screenshot", self)
        action.setShortcut("Ctrl+P")
        action.setStatusTip("Take screenshot")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action


    def rootModeAction(self):
        action = QAction("&Root mode", self)
        action.setStatusTip("Enable/disable root mode")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(True)
        action.setData(False)
        return action

    def rebootDeviceAction(self):
        action = QAction("&Reboot device", self)
        action.setStatusTip("Reboot device")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(True)
        action.setData(False)
        return action

    def shutdownDeviceAction(self):
        action = QAction("&Shutdown device", self)
        action.setStatusTip("Shutdown device")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(True)
        action.setData(False)
        return action

    def setupMenuBar(self):
        menuBar = self.menuBar()
        captureMenu = menuBar.addMenu("📱 &Capture")
        captureMenu.addAction(self.startCaptureAction())
        captureMenu.addAction(self.stopCaptureAction())
        captureMenu.addAction(self.openLogFileAction())
        captureMenu.addAction(self.saveLogFileAction())
        captureMenu.addAction(self.messageFilterAction())
        captureMenu.addAction(self.liveReloadAction())
        captureMenu.addAction(self.showLineNumbersAction())

        adbMenu = menuBar.addMenu("🐞 &ADB")
        adbMenu.addAction(self.installApkAction())
        adbMenu.addAction(self.takeScreenshotAction())
        adbMenu.addAction(self.rootModeAction())
        adbMenu.addAction(self.rebootDeviceAction())
        adbMenu.addAction(self.shutdownDeviceAction())

        self.increaseHoverAreaForCheckableActions()

    def initUserInterface(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        pane = LogMessagesPane(self)
        self.logMessagesPaneController.takeControl(pane)
        self.setCentralWidget(pane)
        self.setWindowTitle("galog")
        self.setWindowIcon(QIcon(iconFile("galog")))

        self.setupMenuBar()
        self.statusBar().show()
