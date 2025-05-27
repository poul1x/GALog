from typing import Callable, List, Optional

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QFocusEvent, QKeyEvent, QMouseEvent, QGuiApplication
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
from galog.app.ui.base.item_view_proxy import ScrollHint
from galog.app.ui.quick_dialogs.loading_dialog import LoadingDialog

from galog.app.ui.reusable.search_input.widget import SearchInput
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from galog.app.ui.base.widget import Widget

from .log_messages_table import LogMessagesTable, Column
from .quick_filter_bar import FilterField, QuickFilterBar


class LogMessagesPanel(Widget):
    captureInterrupted = pyqtSignal(str, str)

    def __init__(self, appState: AppState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initFocusPolicy()
        self._appState = appState
        self._liveReload = True
        self._logReader = None
        self._lineNumbersAlwaysVisible = False
        self._lastFilterRowNum = -1

    def _initUserInputHandlers(self):
        self._logMessagesTable.requestCopyLogLines.connect(
            self._copySelectedLogLinesToClipboard
        )

        self._logMessagesTable.requestCopyLogMessages.connect(
            self._copySelectedLogMessagesToClipboard
        )

        self._logMessagesTable.requestShowOriginalLine.connect(
            self._showOriginalLogLine
        )

        self._logMessagesTable.requestShowFilteredLine.connect(
            self._showLastFilteredLogLine
        )

        self._quickFilterBar.arrowUpPressed.connect(self._tryFocusLogMessagesTableAndGoUp)
        self._quickFilterBar.arrowDownPressed.connect(self._tryFocusLogMessagesTableAndGoDown)

    def _initUserInterface(self):
        layout = QVBoxLayout()
        self._logMessagesTable = LogMessagesTable(self)
        self._quickFilterBar = QuickFilterBar(self)
        self._quickFilterBar.startSearch.connect(self.quickFilterApply)

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
        action = GetAppPidsAction(self._adbClient())
        action.setLoadingDialogText("Fetching App Logs...")
        pids = action.appPids(device, package)
        if pids is None:
            return

        if pids:
            msg = f"App '{package}' is running. PID(s): {', '.join(pids)}"
            self._addOwnLogLine(msg)
        else:
            msg = f"App '{package}' is not running. Waiting for its start..."
            self._addOwnLogLine(msg)

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
        self._logMessagesTable.addLogLine(line)

    def _addOwnLogLine(self, message: str):
        logLine = LogLine("GALog", "S", message, -1)
        self._logMessagesTable.addLogLine(logLine)

    def _appStarted(self, packageName: str):
        if self._liveReload:
            self.clearLogLines()

        msg = f"App '{packageName}' started"
        self._addOwnLogLine(msg)

    def _processStarted(self, event: ProcessStartedEvent):
        msg = f"Process <PID={event.processId}> started for {event.target}"
        self._addOwnLogLine(msg)

    def _processEnded(self, event: ProcessEndedEvent):
        msg = f"Process <PID={event.processId}> ended"
        self._addOwnLogLine(msg)

    def _appEnded(self, packageName: str):
        msg = f"App '{packageName}' ended"
        self._addOwnLogLine(msg)

    def _logReaderFailed(self, msgBrief: str, msgVerbose: str):
        self.stopCapture()
        self.captureInterrupted.emit(msgBrief, msgVerbose)

    def clearLogLines(self):
        self._logMessagesTable.clearLogLines()

    def addLogLines(self, logLines: List[LogLine]):
        self._logMessagesTable.addLogLines(logLines)

    def setWhiteBackground(self):
        self._logMessagesTable.setWhiteBackground()

    def setHighlightingEnabled(self, enabled: bool):
        self._logMessagesTable.setHighlightingEnabled(enabled)

    ###################

    def quickFilterApply(self, filterField: FilterField, filterText: str):
        if filterField == FilterField.Message:
            self._logMessagesTable.quickFilterApply(Column.logMessage, filterText)
        elif filterField == FilterField.Tag:
            self._logMessagesTable.quickFilterApply(Column.tagName, filterText)
        else:  # Level
            self._logMessagesTable.quickFilterApply(Column.logLevel, filterText)

    def quickFilterReset(self):
        self._logMessagesTable.quickFilterReset()
        self._quickFilterBar.reset()

    def advancedFilterApply(self, fn: Callable[[str], bool]):
        self._logMessagesTable.advancedFilterApply(fn)

    def advancedFilterReset(self):
        self._logMessagesTable.advancedFilterReset()

    #####

    def setLineNumbersAlwaysVisible(self, visible: bool):
        self._lineNumbersAlwaysVisible = visible
        self._logMessagesTable.setLineNumbersVisible(visible)

    def hasLogMessages(self):
        return self._logMessagesTable.hasItems()

    def enableQuickFilter(self):

        # if self._beforeFilterRow == -1:
        #     assert self.hasLogMessages()
        #     selectedRows = self._logMessagesTable.selectedRows()

        #     selectedRows = self._logMessagesTable()

        #     if selectedRows:
        #         self._beforeFilterRow = selectedRows[0]

        self._logMessagesTable.setLineNumbersVisible(True)
        self._logMessagesTable.setQuickFilterEnabled(True)
        self._quickFilterBar.show()
        self._quickFilterBar.setFocus()

    def disableQuickFilter(self, reset: bool = True):

        if reset:
            self._unsetLastFilterRowNum()

        if not self._lineNumbersAlwaysVisible:
            self._logMessagesTable.setLineNumbersVisible(False)

        self._logMessagesTable.setQuickFilterEnabled(False)
        self._logMessagesTable.setFocus()
        self._quickFilterBar.hide()
        self.layout().activate()

    def quickFilterEnabled(self):
        return self._logMessagesTable.quickFilterEnabled()

    #####

    def _initFocusPolicy(self):
        self._quickFilterBar.setFocusPolicy(Qt.StrongFocus)
        self._logMessagesTable.setFocusPolicy(Qt.StrongFocus)

        self.setTabOrder(self._quickFilterBar, self._logMessagesTable)
        self.setTabOrder(self._logMessagesTable, self._quickFilterBar)
        self._logMessagesTable.setFocus()

    def focusInEvent(self, event: QFocusEvent) -> None:
        self._logMessagesTable.setFocus()
        event.accept()

    #####

    def _copyTextToClipboard(self, text: str):
        QGuiApplication.clipboard().setText(text)

    def _copySelectedLogLinesToClipboard(self):
        result = []
        for logLine in self._logMessagesTable.selectedLogLines():
            result.append(f"{logLine.level}/{logLine.tag}: {logLine.msg}")

        self._copyTextToClipboard("\n".join(result))

    def _copySelectedLogMessagesToClipboard(self):
        result = self._logMessagesTable.selectedLogMessages()
        self._copyTextToClipboard("\n".join(result))

    #####

    def _setLastFilterRowNum(self, row: int):
        self._lastFilterRowNum = row

    def _unsetLastFilterRowNum(self):
        self._setLastFilterRowNum(-1)

    def _hasLastFilterRowNum(self):
        return self._lastFilterRowNum != -1

    def _showOriginalLogLine(self):

        if not self._logMessagesTable.quickFilterEnabled():
            return

        selectedRows = self._logMessagesTable.selectedRows()
        assert len(selectedRows) > 0
        selectedRow = selectedRows[0]
        self._setLastFilterRowNum(selectedRow)

        sourceRow = self._logMessagesTable.resolveOriginalRow(selectedRow)

        self.disableQuickFilter(reset=False)
        self._logMessagesTable.selectRow(sourceRow, ScrollHint.PositionAtCenter)
        self._logMessagesTable.startRowBlinking(sourceRow)


    def _showLastFilteredLogLine(self):

        # Disable filter if escape pressed many times
        if not self._hasLastFilterRowNum():
            if self._logMessagesTable.quickFilterEnabled():
                self.disableQuickFilter()
            return

        self.enableQuickFilter()

        self._logMessagesTable.selectRow(self._lastFilterRowNum)
        self._logMessagesTable.setFocus()

        self._logMessagesTable.startRowBlinking(self._lastFilterRowNum)
        self._unsetLastFilterRowNum()

    #####

    def _tryFocusLogMessagesTableAndGoUp(self):
        self._logMessagesTable.trySetFocusAndGoUp()

    def _tryFocusLogMessagesTableAndGoDown(self):
        self._logMessagesTable.trySetFocusAndGoDown()