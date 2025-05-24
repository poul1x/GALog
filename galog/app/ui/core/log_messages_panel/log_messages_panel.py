from typing import List, Optional

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from galog.app.app_state import AppState
from galog.app.device.device import AdbClient
from galog.app.hrules import HRulesStorage
from galog.app.log_reader import AndroidAppLogReader, LogLine
from galog.app.log_reader import ProcessEndedEvent, ProcessStartedEvent
from galog.app.msgbox import msgBoxErr
from galog.app.ui.actions.get_app_pids import GetAppPidsAction
from galog.app.ui.quick_dialogs.loading_dialog import LoadingDialog

from galog.app.ui.reusable.search_input.widget import SearchInput
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from galog.app.ui.base.widget import BaseWidget

from .log_messages_table import LogMessagesTable
from .quick_filter_bar import QuickFilterBar


class LogMessagesPanel(BaseWidget):
    toggleMessageFilter = pyqtSignal()
    copyMsgRowsToClipboard = pyqtSignal()
    copyFullRowsToClipboard = pyqtSignal()
    cmViewMessage = pyqtSignal(QModelIndex)
    cmGoToOrigin = pyqtSignal(QModelIndex)
    cmGoBack = pyqtSignal()

    captureInterrupted = pyqtSignal(str, str)

    def __init__(self, appState: AppState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initUserInterface()
        self._initFocusPolicy()
        self._appState = appState
        self._liveReload = True
        self._logReader = None

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEscapePressed():
            self.toggleMessageFilter.emit()
        elif helper.isCtrlShiftCPressed():
            self.copyFullRowsToClipboard.emit()
        elif helper.isCtrlCPressed():
            self.copyMsgRowsToClipboard.emit()
        else:
            super().keyPressEvent(event)

    def _initFocusPolicy(self):
        # self.searchPane.button.setFocusPolicy(Qt.NoFocus)
        # self.searchPane.searchByDropdown.setFocusPolicy(Qt.NoFocus)
        # self.searchPane.input.setFocusPolicy(Qt.StrongFocus)
        # self.searchPane.setFocusPolicy(Qt.StrongFocus)

        self.setTabOrder(self._logMessagesTable, self._quickFilterBar.searchInput)
        self.setTabOrder(
            self._quickFilterBar.searchInput, self._logMessagesTable._tableView
        )

    def _initUserInterface(self):
        layout = QVBoxLayout()
        self._logMessagesTable = LogMessagesTable(self)
        self._quickFilterBar = QuickFilterBar(self)
        layout.addWidget(self._logMessagesTable, 1)
        layout.addWidget(self._quickFilterBar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def setHighlightingRules(self, hrules: HRulesStorage):
        self._logMessagesTable.setHighlightingRules(hrules)

    def _adbClient(self):
        return AdbClient(
            self._appState.adb.ipAddr,
            int(self._appState.adb.port),
        )

    def startCapture(self, device: str, package: str):
        action = GetAppPidsAction(self._adbClient(), self)
        pids = action.appPids(device, package)
        if pids is None:
            return

        if pids:
            msg = f"App '{package}' is running. PID(s): {', '.join(pids)}"
            self._addLogLine("S", "galog", msg)
        else:
            msg = f"App '{package}' is not running. Waiting for its start..."
            self._addLogLine("S", "galog", msg)

        self._logReader = AndroidAppLogReader(self._adbClient(), device, package, pids)
        self._logReader.signals.failed.connect(self._logReaderFailed)
        self._logReader.signals.appStarted.connect(self._appStarted)
        self._logReader.signals.appEnded.connect(self._appEnded)
        self._logReader.signals.processStarted.connect(self._processStarted)
        self._logReader.signals.processEnded.connect(self._processEnded)
        self._logReader.signals.lineRead.connect(self._lineRead)
        self._logReader.start()

    def stopCapture(self):
        if self._logReader:
            self._logReader.stop()
            self._logReader = None

    def isCaptureRunning(self):
        return self._logReader and self._logReader.isRunning()

    def setLiveReloadEnabled(self, enabled: bool):
        self._liveReload = enabled

    def _lineRead(self, line: LogLine):
        self._addLogLine(line.level, line.tag, line.msg)

    def _addLogLine(self, tagName: str, logLevel: str, message: str):
        self._logMessagesTable.addLogLine(tagName, logLevel, message)

    def _appStarted(self, packageName: str):
        if self._liveReload:
            self.clearLogLines()
            # self.disableMessageFilter()

        msg = f"App '{packageName}' started"
        self._addLogLine("S", "galog", msg)

    def _processStarted(self, event: ProcessStartedEvent):
        msg = f"Process <PID={event.processId}> started for {event.target}"
        self._addLogLine("S", "galog", msg)

    def _processEnded(self, event: ProcessEndedEvent):
        msg = f"Process <PID={event.processId}> ended"
        self._addLogLine("S", "galog", msg)

    def _appEnded(self, packageName: str):
        msg = f"App '{packageName}' ended"
        self._addLogLine("S", "galog", msg)

    def _logReaderFailed(self, msgBrief: str, msgVerbose: str):
        self.stopCapture()
        self.captureInterrupted.emit(msgBrief, msgVerbose)


    def clearLogLines(self):
        self._logMessagesTable.clearLogLines()

    def setWhiteBackground(self):
        self._logMessagesTable.setWhiteBackground()

    def setHighlightingEnabled(self, enabled: bool):
        self._logMessagesTable.setHighlightingEnabled(enabled)