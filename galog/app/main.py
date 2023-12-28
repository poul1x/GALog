import sys
import shutil
import subprocess
import tarfile
from contextlib import suppress
from typing import List, Optional

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication


from galog.app.components.capture_pane import CapturePane, RunAppAction
from galog.app.components.dialogs.stop_capture_dialog import (
    StopCaptureDialog,
    StopCaptureDialogResult,
)
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.controllers.capture_pane import CapturePaneController
from galog.app.controllers.install_app import InstallAppController
from galog.app.controllers.kill_app import KillAppController
from galog.app.controllers.log_messages_pane.controller import LogMessagesPaneController
from galog.app.controllers.run_app.controller import RunAppController
from galog.app.highlighting import HighlightingRules
from galog.app.util.message_box import (
    showErrorMsgBox,
    showNotImpMsgBox,
    showPromptMsgBox,
)
from galog.app.util.paths import fontFiles, highlightingFiles, iconFile, styleSheetFiles
from galog.app.util.style import CustomStyle

from .strings import appStringsInit
from .components.log_messages_pane import LogMessagesPane

ADB_HOST = "127.0.0.1"
ADB_PORT = 5037


class MainWindow(QMainWindow):
    _viewWindows: List[LogMessageViewPane]
    _liveReload: bool

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("MainWindow")
        self.setStyle(CustomStyle())
        self.startAdbServer()
        self._searchPane = None
        self._liveReload = True
        self.capturePaneController = CapturePaneController(ADB_HOST, ADB_PORT)
        self.logMessagesPaneController = LogMessagesPaneController(ADB_HOST, ADB_PORT)
        self.loadAppStrings()
        self.loadStyleSheet()
        self.loadFonts()
        self.initHighlighting()
        self.initUserInterface()
        self.initLeftPaddingForEachMenu()
        self.increaseHoverAreaForCheckableActions()

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
        appStringsInit("en")

    def loadFontsFromTar(self, fontDB: QFontDatabase, tar: tarfile.TarFile):
        for member in tar.getmembers():
            if member.path.endswith(".ttf"):
                with tar.extractfile(member) as f:
                    fontDB.addApplicationFontFromData(f.read())

    def loadFonts(self):
        fontDB = QFontDatabase()
        for archive in fontFiles():
            with tarfile.open(archive, "r") as tar:
                self.loadFontsFromTar(fontDB, tar)

    def loadStyleSheet(self):
        styleSheet = ""
        for filepath in styleSheetFiles():
            with open(filepath, "r", encoding="utf-8") as f:
                styleSheet += f.read() + "\n"

        self.setStyleSheet(styleSheet)

    def initHighlighting(self):
        rules = HighlightingRules()
        for filepath in highlightingFiles():
            rules.addRuleset(filepath)

        self.logMessagesPaneController.setHighlightingRules(rules)

    def closeEvent(self, event: QEvent):
        if showPromptMsgBox(
            title="Close window",
            caption="Do you really want to quit?",
            body="If you close the window, current progress will be lost",
        ):
            self.logMessagesPaneController.stopCapture()
            event.accept()
        else:
            event.ignore()

    def setCaptureSpecificActionsEnabled(self, enabled: bool):
        menuBar = self.menuBar()
        for fileMenu in menuBar.findChildren(QMenu):
            for action in fileMenu.actions():
                if action.data() == True:
                    action.setEnabled(enabled)

    def getCheckBoxRectWidthWithSpacing(self, checkBox: QCheckBox):
        return self.getCheckBoxRectWidth(checkBox) + self.getCheckBoxLabelSpacing(checkBox)  # fmt: skip

    def initMenuLeftPadding(self, menu: QMenu):
        paddingLeft = 30  # default
        for action in menu.actions():
            if isinstance(action, QWidgetAction):
                defaultWidget = action.defaultWidget()
                if isinstance(defaultWidget, QCheckBox):
                    paddingLeft = self.getCheckBoxRectWidthWithSpacing(defaultWidget)
                    break

        menu.setStyleSheet("QMenu::item { padding-left: %dpx; }" % paddingLeft)

    def initLeftPaddingForEachMenu(self):
        menuBar = self.menuBar()
        for menu in menuBar.findChildren(QMenu):
            self.initMenuLeftPadding(menu)

    def increaseHoverAreaForCheckableActions(self):
        menuBar = self.menuBar()
        for menu in menuBar.findChildren(QMenu):
            for action in menu.actions():
                if isinstance(action, QWidgetAction):
                    defaultWidget = action.defaultWidget()
                    if isinstance(defaultWidget, QCheckBox):
                        # hacky & dirty way to make entire line hoverable
                        defaultWidget.setText(defaultWidget.text() + " " * 64)
                        defaultWidget.setStyleSheet("width: 0px;")

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
                # controller.setAppDebug(action == RunAppAction.StartAppDebug)
                controller.setAppDebug(False)
                controller.runApp(device, package)

            self.logMessagesPaneController.startCapture(device, package)
            self.setCaptureSpecificActionsEnabled(True)

    def clearCaptureOutput(self):
        if showPromptMsgBox(
            title="Clear capture output",
            caption="Clear capture output?",
            body="All captured log messages will be erased",
        ):
            self.logMessagesPaneController.clearLogMessages()

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

    def restartCaptureAction(self):
        action = QAction("&Restart", self)
        action.setShortcut("Ctrl+R")
        action.setStatusTip("Restart log capture (with app restart)")
        action.triggered.connect(lambda: showNotImpMsgBox())
        action.setEnabled(False)
        action.setData(True)
        return action

    def messageFilterAction(self):
        action = QAction("&Find", self)
        action.setShortcut("Ctrl+F")
        action.setStatusTip("Show message filter (hide with ESC)")
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

    def clearCaptureOutputAction(self):
        action = QAction("&Clear", self)
        action.setShortcut("Ctrl+X")
        action.setStatusTip("Clear capture output")
        action.triggered.connect(lambda: self.clearCaptureOutput())
        action.setEnabled(True)
        action.setData(False)
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

    def getCheckBoxRectWidth(self, checkBox: QCheckBox):
        option = QStyleOptionButton()
        option.initFrom(checkBox)
        style = checkBox.style()
        rect = style.subElementRect(QStyle.SE_CheckBoxIndicator, option, checkBox)
        return rect.width()

    def getCheckBoxLabelSpacing(self, checkBox: QCheckBox):
        return checkBox.style().pixelMetric(
            QStyle.PM_CheckBoxLabelSpacing, None, checkBox
        )

    def liveReloadAction(self):
        action = QWidgetAction(self)
        checkBox = QCheckBox("Live reload")
        checkBox.stateChanged.connect(lambda: self.toggleLiveReload(checkBox))
        checkBox.setChecked(True)

        action.setDefaultWidget(checkBox)
        action.setStatusTip("Enable/disable log pane reload on app restart")
        action.setEnabled(True)
        action.setData(False)
        return action

    def showLineNumbersAction(self):
        action = QWidgetAction(self)
        checkBox = QCheckBox("Show line numbers")
        checkBox.stateChanged.connect(lambda: self.toggleShowLineNumbers(checkBox))
        checkBox.setChecked(False)
        self.checkBox = checkBox

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
        captureMenu.addAction(self.restartCaptureAction())
        captureMenu.addAction(self.stopCaptureAction())
        captureMenu.addAction(self.clearCaptureOutputAction())
        captureMenu.addAction(self.openLogFileAction())
        captureMenu.addAction(self.saveLogFileAction())
        captureMenu.addAction(self.messageFilterAction())
        captureMenu.addAction(self.liveReloadAction())
        captureMenu.addAction(self.showLineNumbersAction())

        # This will be implemented in the next release
        # adbMenu = menuBar.addMenu("🐞 &ADB")
        # adbMenu.addAction(self.installApkAction())
        # adbMenu.addAction(self.takeScreenshotAction())
        # adbMenu.addAction(self.rootModeAction())
        # adbMenu.addAction(self.rebootDeviceAction())
        # adbMenu.addAction(self.shutdownDeviceAction())

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


def runApp():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
