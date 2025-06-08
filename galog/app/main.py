import shutil
import subprocess
import sys
import tarfile
from contextlib import suppress
from typing import Dict, List

import traceback
import os
import shutil

from PyQt5.QtCore import QEvent, QThread, QThreadPool, QStandardPaths
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

from galog.app.app_state import (
    AdbServerSettings,
    AppState,
    RunAppAction,
    TagFilteringConfig,
    TagFilteringMode,
)
from galog.app.ui.actions.stop_app import StopAppAction
from galog.app.ui.core.device_select_dialog import DeviceSelectDialog
from galog.app.ui.quick_dialogs import (
    RestartCaptureDialog,
)
from galog.app.ui.quick_dialogs.stop_capture_dialog import (
    StopCaptureDialog,
    StopCaptureDialogResult,
)

# from galog.app.ui.core.message_view_dialog import LogMessageViewDialog
from galog.app.ui.core.package_select_dialog import PackageSelectDialog
from galog.app.ui.core.log_messages_panel import LogMessagesPanel
from galog.app.ui.actions.read_log_file.action import ReadLogFileAction
from galog.app.ui.actions.restart_app.action import RestartAppAction
from galog.app.ui.actions.start_app import StartAppAction
from galog.app.ui.actions.write_log_file.action import WriteLogFileAction

from galog.app.ui.core.tag_filter_dialog import TagFilterDialog
from galog.app.device.device import AdbClient
from galog.app.hrules import HRulesStorage
from galog.app.logging import initLogging
from galog.app.msgbox import (
    msgBoxErr,
    msgBoxInfo,
    msgBoxNotImp,
    msgBoxPrompt,
)
from galog.app.paths import (
    appConfigDir,
    appLogsDir,
    appLogsRootDir,
    appSessionID,
    fontFiles,
    highlightingFiles,
    iconFile,
    loggingConfigFile,
    loggingConfigFileInitial,
    styleSheetFiles,
    appDataDir,
    fixUrlPaths,
)
from galog.app.ui.base.style import GALogStyle

from galog.app.ui.core.log_messages_panel import LogMessagesPanel
from galog.app.ui.reusable.file_picker import FilePicker, FileExtensionFilterBuilder


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initAppState()
        self.setObjectName("MainWindow")
        self.setStyle(GALogStyle())
        self.loadFonts()
        self.initUserInterface()
        self.initHighlighting()
        self.initLeftPaddingForEachMenu()
        self.increaseHoverAreaForCheckableActions()
        self.startAdbServer()

    def initAppState(self):
        self.appState = AppState(
            adb=AdbServerSettings(
                ipAddr="127.0.0.1",
                port=5037,
            ),
            lastSelectedDevice=None,
            lastSelectedPackage=None,
            tagFilteringConfig=TagFilteringConfig.none(),
            lastUsedDirPath="",
        )

    def isLocalAdbAddr(self):
        return self.appState.adb.ipAddr.startswith("127")

    def startAdbServer(self):
        adb = shutil.which("adb")
        if not adb:
            return

        if not self.isLocalAdbAddr():
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

    def initHighlighting(self):
        rules = HRulesStorage()
        for filepath in highlightingFiles():
            rules.addRuleSet(filepath)

        self.logMessagesPanel.setHighlightingRules(rules)

    def cancelThreadPoolTasks(self):
        QThreadPool.globalInstance().clear()
        QThreadPool.globalInstance().waitForDone()

    def closeEvent(self, event: QEvent):
        if msgBoxPrompt(
            caption="Do you really want to quit?",
            body="If you close the window, current progress will be lost",
            parent=self,
        ):
            self.logMessagesPanel.stopCapture()
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
        dialog = TagFilterDialog(self.appState, self)
        tagList = self.logMessagesPanel.uniqueTagNames()
        dialog.setTagAutoCompletionStrings(tagList)

        if dialog.exec_() == TagFilterDialog.Rejected:
            return

        config = self.appState.tagFilteringConfig
        if config.mode == TagFilteringMode.ShowMatching:
            self.logMessagesPanel.advancedFilterApply(lambda tag: tag in config.tags)
        elif config.mode == TagFilteringMode.HideMatching:
            self.logMessagesPanel.advancedFilterApply(
                lambda tag: tag not in config.tags
            )
        else:  # config.mode == TagFilteringMode.Disabled:
            self.logMessagesPanel.advancedFilterReset()

    def showDevices(self):
        deviceSelectPane = DeviceSelectDialog(self.appState, self)
        deviceSelectPane.exec_()

    def startCapture(self):
        if self.logMessagesPanel.isCaptureRunning():
            msgBrief = "Capture is running"
            msgVerbose = "Unable to start capture while another capture is running. Please, stop the running capture first"  # fmt: skip
            msgBoxErr(msgBrief, msgVerbose, self)
            return

        if self.appState.lastSelectedDevice is None:
            deviceSelectPane = DeviceSelectDialog(self.appState, self)
            deviceSelectPane.setDeviceAutoSelect(True)
            if deviceSelectPane.exec_() == DeviceSelectDialog.Rejected:
                msgBrief = "Device not selected"
                msgVerbose = "Device was not selected. Unable to start log capture"  # fmt: skip
                msgBoxInfo(msgBrief, msgVerbose, self)
                return

            # Add small delay to remove
            # LoadingDialog flickering
            QThread.msleep(100)

        packageSelectDialog = PackageSelectDialog(self.appState, self)
        result = packageSelectDialog.exec_()
        if result == 0:
            return

        device = self.appState.lastSelectedDevice.serial
        package = self.appState.lastSelectedPackage.name
        action = self.appState.lastSelectedPackage.action

        if action != RunAppAction.DoNotStartApp:
            _action = StartAppAction(self.adbClient(), self)
            _action.startApp(device, package)
            if _action.failed():
                return

        self.logMessagesPanel.setWhiteBackground()
        self.logMessagesPanel.disableQuickFilter()
        self.logMessagesPanel.clearLogLines()

        self.setCaptureSpecificActionsEnabled(True)
        self.logMessagesPanel.startCapture(device, package)

    def clearCaptureOutput(self):
        if msgBoxPrompt(
            caption="Clear capture output?",
            body="All captured log messages will be erased",
            parent=self,
        ):
            self.logMessagesPanel.setWhiteBackground()
            self.logMessagesPanel.disableQuickFilter()
            self.logMessagesPanel.clearLogLines()

    def _saveLastSelectedDir(self, filePicker: FilePicker):
        if filePicker.hasSelectedDirectory():
            self.appState.lastUsedDirPath = filePicker.selectedDirectory()

    def saveLogFile(self):
        filePicker = FilePicker(
            caption="Save log lines to file",
            directory=self.appState.lastUsedDirPath,
            extensionFilter=FileExtensionFilterBuilder.logFile(),
        )

        filePath = filePicker.askOpenFileWrite()
        if not filePath:
            return

        self._saveLastSelectedDir(filePicker)
        self.logMessagesPanel.saveLogFile(filePath)

    def openLogFile(self):
        if self.logMessagesPanel.isCaptureRunning():
            msgBrief = "Capture is running"
            msgVerbose = "Unable to open log file while capture is running. Please, stop the running capture first"  # fmt: skip
            msgBoxErr(msgBrief, msgVerbose, self)
            return

        filePicker = FilePicker(
            caption="Load log lines from file",
            directory=self.appState.lastUsedDirPath,
            extensionFilter=FileExtensionFilterBuilder.logFile(),
        )

        filePath = filePicker.askOpenFileRead()
        if not filePath:
            return

        self._saveLastSelectedDir(filePicker)
        self.logMessagesPanel.clearLogLines()
        self.logMessagesPanel.setWhiteBackground()
        self.logMessagesPanel.disableQuickFilter()
        self.logMessagesPanel.loadLogFile(filePath)

    def restartCapture(self):
        dialog = RestartCaptureDialog(self)
        result = dialog.exec_()
        if result == RestartCaptureDialog.Rejected:
            return

        assert self.appState.lastSelectedDevice is not None
        device = self.appState.lastSelectedDevice.serial
        package = self.appState.lastSelectedPackage.name
        # mode = self.appState.lastSelectedPackage.action

        self.logMessagesPanel.stopCapture()
        self.logMessagesPanel.setWhiteBackground()
        # self.logMessagesPanel.disableMessageFilter()
        self.logMessagesPanel.clearLogLines()

        action = RestartAppAction(self.adbClient())
        action.restartApp(device, package)
        if action.failed():
            return

        self.logMessagesPanel.startCapture(device, package)

    def adbClient(self):
        return AdbClient(
            self.appState.adb.ipAddr,
            int(self.appState.adb.port),
        )

    def stopCapture(self):
        dialog = StopCaptureDialog(self)
        result = dialog.exec_()
        if result == StopCaptureDialog.Rejected:
            return

        if result == StopCaptureDialog.AcceptedStopApp:
            device = self.appState.lastSelectedDevice.serial
            package = self.appState.lastSelectedPackage.name
            #
            # Ignore action.failed(), because we want
            # to stop the capture anyway
            #
            action = StopAppAction(self.adbClient(), self)
            action.stopApp(device, package)

        self.logMessagesPanel.stopCapture()
        self.setCaptureSpecificActionsEnabled(False)

    def enableQuickFilter(self):
        if self.logMessagesPanel.hasLogMessages():
            self.logMessagesPanel.enableQuickFilter()

    def toggleLiveReload(self, checkBox: QCheckBox):
        self.logMessagesPanel.setLiveReloadEnabled(checkBox.isChecked())

    def toggleHighlighting(self, checkBox: QCheckBox):
        self.logMessagesPanel.setHighlightingEnabled(checkBox.isChecked())

    def toggleShowLineNumbers(self, checkBox: QCheckBox):
        self.logMessagesPanel.setLineNumbersAlwaysVisible(checkBox.isChecked())

    # def handleInstallApkAction(self):
    #     device = self.capturePaneController.selectedDevice()
    #     if device is None:
    #         msgBrief = "Operation failed"
    #         msgVerbose = "No device selected (Select device in 'Capture->New' [tmp])"
    #         showErrorMsgBox(msgBrief, msgVerbose)
    #         return

    #     controller = InstallAppController()
    #     controller.promptInstallApp(device)

    def openTagFilterAction(self):
        action = QAction("&Tag filter", self)
        action.setShortcut("Ctrl+Shift+F")
        action.setStatusTip("Open tag filter")
        action.triggered.connect(lambda: self.openTagFilter())
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

    def restartCaptureAction(self):
        action = QAction("&Restart", self)
        action.setShortcut("Ctrl+R")
        action.setStatusTip("Restart capture")
        action.triggered.connect(self.restartCapture)
        action.setEnabled(False)
        action.setData(True)
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
        action.triggered.connect(lambda: self.enableQuickFilter())
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

    # def installApkAction(self):
    #     action = QAction("&Install APK", self)
    #     action.setShortcut("Ctrl+I")
    #     action.setStatusTip("Install app from APK file")
    #     action.triggered.connect(self.handleInstallApkAction)
    #     action.setEnabled(True)
    #     action.setData(False)
    #     return action

    def clearAppDataAction(self):
        action = QAction("&Clear app data", self)
        action.setShortcut("Ctrl+P")
        action.setStatusTip("Clear user data associated with the app")
        action.triggered.connect(lambda: msgBoxNotImp(self))
        action.setEnabled(False)
        action.setData(True)
        return action

    def takeScreenshotAction(self):
        action = QAction("&Take screenshot", self)
        action.setShortcut("Ctrl+P")
        action.setStatusTip("Take screenshot")
        action.triggered.connect(lambda: msgBoxNotImp(self))
        action.setEnabled(False)
        action.setData(True)
        return action

    def rootModeAction(self):
        action = QAction("&Root mode", self)
        action.setStatusTip("Enable/disable root mode")
        action.triggered.connect(lambda: msgBoxNotImp(self))
        action.setEnabled(True)
        action.setData(False)
        return action

    def rebootDeviceAction(self):
        action = QAction("&Reboot device", self)
        action.setStatusTip("Reboot device")
        action.triggered.connect(lambda: msgBoxNotImp(self))
        action.setEnabled(True)
        action.setData(False)
        return action

    def shutdownDeviceAction(self):
        action = QAction("&Shutdown device", self)
        action.setStatusTip("Shutdown device")
        action.triggered.connect(lambda: msgBoxNotImp(self))
        action.setEnabled(True)
        action.setData(False)
        return action

    def setupMenuBar(self):
        menuBar = self.menuBar()
        captureMenu = menuBar.addMenu("📱 &Capture")
        captureMenu.addAction(self.showDevicesAction())
        captureMenu.addAction(self.startCaptureAction())
        captureMenu.addAction(self.restartCaptureAction())
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

    def captureInterrupted(self, msgBrief: str, msgVerbose: str):
        self.setCaptureSpecificActionsEnabled(False)
        msgBoxErr(msgBrief, msgVerbose, self)

    def initUserInterface(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        self.logMessagesPanel = LogMessagesPanel(self.appState, self)
        self.logMessagesPanel.captureInterrupted.connect(self.captureInterrupted)

        self.setCentralWidget(self.logMessagesPanel)
        self.setWindowTitle("GALog")
        self.setWindowIcon(QIcon(iconFile("GALog")))

        self.setupMenuBar()
        self.statusBar().show()


def tryInitLogging():
    try:
        initLogging()
    except:
        traceback.print_exc()
        msgBrief = "Logging not available"
        msgVerbose = "Failed to init logging. Logging will not be available"
        msgBoxErr(msgBrief, msgVerbose)


def createAppDataFolders():
    dataDir = appDataDir()
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)

    configDir = appConfigDir()
    if not os.path.exists(configDir):
        os.mkdir(configDir)

    logsRootDir = appLogsRootDir()
    if not os.path.exists(logsRootDir):
        os.mkdir(logsRootDir)

    logsDir = appLogsDir()
    if not os.path.exists(logsDir):
        os.mkdir(logsDir)


def createUserAppData():
    userLoggingConfig = loggingConfigFile()
    if not os.path.exists(userLoggingConfig):
        initialLoggingConfig = loggingConfigFileInitial()
        shutil.copy(initialLoggingConfig, userLoggingConfig)


def removeOldLogs():
    sessionId = appSessionID()
    logging.info("Running with sessionID: %s", sessionId)

    rootDir = appLogsRootDir()
    for dirName in os.listdir(rootDir):
        if dirName == sessionId:
            continue

        with suppress(Exception):
            oldLogDir = os.path.join(rootDir, dirName)
            logging.debug("Remove old logs at: '%s'", oldLogDir)
            shutil.rmtree(oldLogDir)


class GALogApp(QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.loadStyleSheetFiles()

    def loadStyleSheetFiles(self):
        styleSheet = ""
        for filePath in styleSheetFiles():
            self._logger.info("Load styleSheet from '%s'", filePath)
            with open(filePath, "r", encoding="utf-8") as f:
                styleSheet += f.read() + "\n"

        self.setStyleSheet(fixUrlPaths(styleSheet))


def preRunApp():
    createAppDataFolders()
    createUserAppData()
    tryInitLogging()
    removeOldLogs()


import logging


def runApp():
    preRunApp()
    app = GALogApp(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
