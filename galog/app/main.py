from dataclasses import dataclass
import shutil
import subprocess
import sys
import tarfile
from contextlib import suppress
from typing import List, Optional

from PyQt5.QtCore import QEvent, QThreadPool
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QMainWindow,
    QMenu,
    QStyle,
    QStyleOptionButton,
    QWidgetAction,
)
from galog.app.app_state import AdbServerSettings, AppState, RunAppAction

from galog.app.components.package_select_pane import PackageSelectPane
from galog.app.components.device_select_pane.pane import DeviceSelectPane
from galog.app.components.dialogs.stop_capture_dialog import (
    StopCaptureDialog,
    StopCaptureDialogResult,
)
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.components.tag_filter_pane.pane import TagFilterPane
from galog.app.controllers.install_app import InstallAppController
from galog.app.controllers.kill_app import KillAppController
from galog.app.controllers.log_messages_pane.controller import LogMessagesPaneController
from galog.app.controllers.open_log_file.controller import OpenLogFileController
from galog.app.controllers.run_app.controller import RunAppController
from galog.app.controllers.save_log_file.controller import SaveLogFileController
from galog.app.controllers.tag_filter_pane.controller import (
    TagFilteringMode,
    TagFilterPaneController,
)
from galog.app.highlighting import HighlightingRules
from galog.app.util.message_box import (
    showErrorMsgBox,
    showInfoMsgBox,
    showNotImpMsgBox,
    showPromptMsgBox,
)
from galog.app.util.paths import fontFiles, highlightingFiles, iconFile, styleSheetFiles
from galog.app.util.style import CustomStyle

from .components.log_messages_pane import LogMessagesPane


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
        self.logMessagesPaneController = LogMessagesPaneController(self)
        self.tagFilterPaneController = TagFilterPaneController(self)
        self.loadStyleSheet()
        self.loadFonts()
        self.initHighlighting()
        self.initUserInterface()
        self.initLeftPaddingForEachMenu()
        self.increaseHoverAreaForCheckableActions()
        self.appState = AppState(
            AdbServerSettings(
                ipAddr="127.0.0.1",
                port=5037,
            ),
            lastSelectedDevice=None,
            lastSelectedPackage=None,
        )

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

    def cancelThreadPoolTasks(self):
        QThreadPool.globalInstance().clear()
        QThreadPool.globalInstance().waitForDone()

    def closeEvent(self, event: QEvent):
        if showPromptMsgBox(
            title="Close window",
            caption="Do you really want to quit?",
            body="If you close the window, current progress will be lost",
        ):
            self.logMessagesPaneController.stopCapture()
            self.cancelThreadPoolTasks()
            event.accept()
        else:
            event.ignore()

    def findActionByName(self, name: str):
        result = None
        for action in self.actions():
            if action.objectName() == name:
                result = action
                break

        return result

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

    def openTagFilter(self):
        tagList = self.logMessagesPaneController.uniqueTagNames()
        result = self.tagFilterPaneController.exec_(tagList)
        if result == TagFilterPane.Rejected:
            return

        config = self.tagFilterPaneController.filteringConfig()
        if config.mode == TagFilteringMode.ShowMatching:
            self.logMessagesPaneController.setTagFilteringFn(
                lambda tag: tag in config.tags
            )
        elif config.mode == TagFilteringMode.HideMatching:
            self.logMessagesPaneController.setTagFilteringFn(
                lambda tag: tag not in config.tags
            )
        else:  # config.mode == TagFilteringMode.Disabled:
            self.logMessagesPaneController.unsetTagFilteringFn()

    def showDevices(self):
        deviceSelectPane = DeviceSelectPane(self.appState, self)
        deviceSelectPane.exec_()

    def startCapture(self):
        if self.logMessagesPaneController.isCaptureRunning():
            msgBrief = "Capture is running"
            msgVerbose = "Unable to start capture while another capture is running. Please, stop the running capture first"  # fmt: skip
            showErrorMsgBox(msgBrief, msgVerbose)
            return

        if self.appState.lastSelectedDevice is None:
            deviceSelectPane = DeviceSelectPane(self.appState, self)
            deviceSelectPane.setDeviceAutoSelect(True)
            if deviceSelectPane.exec_() == DeviceSelectPane.Rejected:
                msgBrief = "Device not selected"
                msgVerbose = "Device was not selected. Unable to start log capture"  # fmt: skip
                showInfoMsgBox(msgBrief, msgVerbose)
                return

        packageSelectPane = PackageSelectPane(self.appState, self)
        result = packageSelectPane.exec_()
        if result == 0:
            return

        device = self.appState.lastSelectedDevice.serial
        package = self.appState.lastSelectedPackage.name
        action = self.appState.lastSelectedPackage.action

        if action != RunAppAction.DoNotStartApp:
            controller = RunAppController()
            # controller.setAppDebug(action == RunAppAction.StartAppDebug)
            controller.setAppDebug(False)
            controller.runApp(device, package)

        self.logMessagesPaneController.makeWhiteBackground()
        self.logMessagesPaneController.disableMessageFilter()
        self.logMessagesPaneController.clearLogLines()
        self.logMessagesPaneController.startCapture(device, package)
        self.setCaptureSpecificActionsEnabled(True)

    def clearCaptureOutput(self):
        if showPromptMsgBox(
            title="Clear capture output",
            caption="Clear capture output?",
            body="All captured log messages will be erased",
        ):
            self.logMessagesPaneController.makeWhiteBackground()
            self.logMessagesPaneController.disableMessageFilter()
            self.logMessagesPaneController.clearLogLines()

    def saveLogFile(self):
        logLines = self.logMessagesPaneController.logLines()
        controller = SaveLogFileController(logLines)
        controller.promptSaveFile()

    def openLogFile(self):
        if self.logMessagesPaneController.isCaptureRunning():
            msgBrief = "Capture is running"
            msgVerbose = "Unable to open log file while capture is running. Please, stop the running capture first"  # fmt: skip
            showErrorMsgBox(msgBrief, msgVerbose)
            return

        controller = OpenLogFileController()
        lines = controller.promptOpenFile()
        if not lines:
            return

        self.logMessagesPaneController.makeWhiteBackground()
        self.logMessagesPaneController.disableMessageFilter()
        self.logMessagesPaneController.clearLogLines()
        self.logMessagesPaneController.addLogLines(lines)

    def stopCapture(self):
        dialog = StopCaptureDialog()
        result = dialog.exec_()
        if result == StopCaptureDialogResult.Rejected:
            return

        if result == StopCaptureDialogResult.AcceptedKillApp:
            device = self.logMessagesPaneController.device
            package = self.logMessagesPaneController.package
            controller = KillAppController()
            controller.killApp(device, package)

        self.logMessagesPaneController.stopCapture()
        self.setCaptureSpecificActionsEnabled(False)

    def enableMessageFilter(self):
        self.logMessagesPaneController.enableMessageFilter()

    def toggleLiveReload(self, checkBox: QCheckBox):
        self.logMessagesPaneController.setLiveReloadEnabled(checkBox.isChecked())

    def toggleHighlighting(self, checkBox: QCheckBox):
        self.logMessagesPaneController.setHighlightingEnabled(checkBox.isChecked())

    def toggleShowLineNumbers(self, checkBox: QCheckBox):
        self.logMessagesPaneController.setShowLineNumbers(checkBox.isChecked())

    def handleInstallApkAction(self):
        device = self.capturePaneController.selectedDevice()
        if device is None:
            msgBrief = "Operation failed"
            msgVerbose = "No device selected (Select device in 'Capture->New' [tmp])"
            showErrorMsgBox(msgBrief, msgVerbose)
            return

        controller = InstallAppController()
        controller.promptInstallApp(device)

    def openTagFilterAction(self):
        action = QAction("&Tag filter", self)
        action.setShortcut("Ctrl+Shift+F")
        action.setStatusTip("Open tag filter")
        action.triggered.connect(lambda: self.openTagFilter())
        # action.setObjectName("capture.new")
        action.setEnabled(True)
        action.setData(False)
        return action

    def startCaptureAction(self):
        action = QAction("&New", self)
        action.setShortcut("Ctrl+N")
        action.setStatusTip("Start new log capture")
        action.triggered.connect(lambda: self.startCapture())
        action.setObjectName("capture.new")
        action.setEnabled(True)
        action.setData(False)
        return action

    def showDevicesAction(self):
        action = QAction("&Devices", self)
        action.setShortcut("Ctrl+D")
        action.setStatusTip("Show devices")
        action.triggered.connect(lambda: self.showDevices())
        action.setEnabled(True)
        action.setData(False)
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
        action.setObjectName("capture.stop")
        action.setEnabled(False)
        action.setData(True)
        return action

    def clearCaptureOutputAction(self):
        action = QAction("&Clear", self)
        action.setShortcut("Ctrl+X")
        action.setStatusTip("Clear capture output")
        action.triggered.connect(lambda: self.clearCaptureOutput())
        action.setObjectName("capture.clear")
        action.setEnabled(True)
        action.setData(False)
        return action

    def openLogFileAction(self):
        action = QAction("&Open", self)
        action.setShortcut("Ctrl+O")
        action.setStatusTip("Open log capture from file")
        action.triggered.connect(lambda: self.openLogFile())
        action.setEnabled(True)
        action.setData(False)
        return action

    def saveLogFileAction(self):
        action = QAction("&Save", self)
        action.setShortcut("Ctrl+S")
        action.setStatusTip("Save log capture to file")
        action.triggered.connect(lambda: self.saveLogFile())
        action.setEnabled(True)
        action.setData(False)
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

    def toggleHighlightingAction(self):
        action = QWidgetAction(self)
        checkBox = QCheckBox("Text highlighting")
        checkBox.stateChanged.connect(lambda: self.toggleHighlighting(checkBox))
        checkBox.setChecked(True)

        action.setDefaultWidget(checkBox)
        action.setStatusTip("Enable/disable text highlighting in log messages pane")
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
        captureMenu.addAction(self.showDevicesAction())
        captureMenu.addAction(self.startCaptureAction())
        captureMenu.addAction(self.stopCaptureAction())
        captureMenu.addAction(self.clearCaptureOutputAction())
        captureMenu.addAction(self.openLogFileAction())
        captureMenu.addAction(self.saveLogFileAction())
        captureMenu.addAction(self.messageFilterAction())
        captureMenu.addAction(self.liveReloadAction())
        captureMenu.addAction(self.toggleHighlightingAction())
        captureMenu.addAction(self.showLineNumbersAction())
        captureMenu.addAction(self.openTagFilterAction())

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
    print("GALog initialized")
    sys.exit(app.exec())
