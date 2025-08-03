from typing import Callable, List, Optional

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QFocusEvent, QGuiApplication
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from galog.app.device.device import adbClient
from galog.app.hrules import HRulesStorage
from galog.app.log_reader import (
    AndroidAppLogReader,
    LogLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)
from galog.app.ui.actions.get_app_pids import GetAppPidsAction
from galog.app.ui.actions.read_log_file import ReadLogFileAction
from galog.app.ui.actions.write_log_file import WriteLogFileAction
from galog.app.ui.base.item_view_proxy import ScrollHint
from galog.app.ui.base.widget import Widget

from .log_messages_table import Column, LogMessagesTable
from .quick_filter_bar import FilterField, QuickFilterBar


class RowBackup:
    INVALID_VALUE: int = -1
    _rowNum: int

    def __init__(self):
        self.delete()

    def setValue(self, rowNum: int):
        assert rowNum >= 0, "Row number must be zero or greater"
        self._rowNum = rowNum

    def getValue(self):
        assert self._rowNum != RowBackup.INVALID_VALUE, "No backup available"
        return self._rowNum

    def empty(self):
        return self._rowNum == RowBackup.INVALID_VALUE

    def delete(self):
        self._rowNum = RowBackup.INVALID_VALUE


class LogMessagesPanel(Widget):
    captureInterrupted = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initCustomContextMenu()
        self._initFocusPolicy()
        self._liveReload = True
        self._logReader = None
        self._lineNumbersAlwaysVisible = False
        self._filterRowBackup = RowBackup()
        self._originalRowBackup = RowBackup()

    def _initUserInputHandlers(self):
        self._logMessagesTable.requestCopyLogLines.connect(
            self._copySelectedLogLinesToClipboard
        )
        self._logMessagesTable.requestCopyLogMessages.connect(
            self._copySelectedLogMessagesToClipboard
        )
        self._logMessagesTable.requestJumpToOriginalLine.connect(
            self._handleJumpToOriginalLine
        )
        self._logMessagesTable.requestJumpBackToFilterView.connect(
            self._handleJumpBackToFilterView
        )

        self._quickFilterBar.arrowUpPressed.connect(
            self._tryFocusLogMessagesTableAndGoUp,
        )
        self._quickFilterBar.arrowDownPressed.connect(
            self._tryFocusLogMessagesTableAndGoDown,
        )
        self._quickFilterBar.escapePressed.connect(
            self._handleJumpBackToFilterView,
        )

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

    def _addAppStateLogLine(self, app: str, pids: List[str]):
        if pids:
            msg = f"App '{app}' is running. PID(s): {', '.join(pids)}"
            self._addOwnLogLine(msg)
        else:
            msg = f"App '{app}' is not running. Waiting for its start..."
            self._addOwnLogLine(msg)

    def startCapture(self, device: str, package: str, pids: List[str]):
        self._addAppStateLogLine(package, pids)
        self._logReader = AndroidAppLogReader(adbClient(), device, package, pids)
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

    def _saveOriginalRow(self):
        assert self.hasLogMessages(), "At least 1 row must be present"
        if self._logMessagesTable.hasSelectedItems():
            selectedRows = self._logMessagesTable.selectedRows()
            self._originalRowBackup.setValue(selectedRows[0])
        else:
            self._originalRowBackup.setValue(0)

    def enableQuickFilter(self, saveRow: bool = True):
        #
        # If Quick filter has been already enabled,
        # just set focus and return
        #

        if self.quickFilterEnabled():
            self._quickFilterBar.setFocus()
            return

        #
        # Save original row to return back
        # if user cancels filtering
        #

        if saveRow:
            self._saveOriginalRow()

        #
        # Show line numbers, show quick filter bar, set focus
        #

        self._logMessagesTable.setLineNumbersVisible(True)
        self._logMessagesTable.setQuickFilterEnabled(True)
        self._quickFilterBar.setFocus()
        self._quickFilterBar.show()

    def disableQuickFilter(self, reset: bool = True):
        #
        # If 'reset' is set to True, delete filter row backup,
        # e.g. start a clean filtering session
        #

        if reset:
            self._filterRowBackup.delete()

        #
        # If 'lineNumbersAlwaysVisible' option is set to True,
        # keep line numbers visible during quick filter disablement
        #

        if not self._lineNumbersAlwaysVisible:
            self._logMessagesTable.setLineNumbersVisible(False)

        #
        # Hide quick filter bar and set focus to log messages table
        #

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

    def _logLineRead(self, logLine: LogLine):
        self._logMessagesTable.addLogLine(logLine)

    def loadLogFile(self, filePath: str):
        action = ReadLogFileAction(filePath)
        action.setLoadingDialogText("Reading log file")
        action.lineRead.connect(self._logLineRead)
        with self._logMessagesTable.enterBatchMode():
            action.readLogFile()

    def saveLogFile(self, filePath: str):
        action = WriteLogFileAction(filePath)
        action.setLoadingDialogText("Saving log output to file")
        action.writeLogFile(self._logMessagesTable.logLines())

    #####

    def _firstSelectedRow(self):
        selectedRows = self._logMessagesTable.selectedRows()
        assert len(selectedRows) > 0
        return selectedRows[0]

    def _handleJumpToOriginalLine(self):
        if not self.quickFilterEnabled():
            return

        #
        # Backup selected row in filter view
        #

        selectedRow = self._firstSelectedRow()
        self._filterRowBackup.setValue(selectedRow)

        #
        # Resolve original row to jump, when quick filter will be disabled
        # Then disable quick filter
        #

        originalRow = self._logMessagesTable.resolveOriginalRow(selectedRow)
        self.disableQuickFilter(reset=False)

        #
        # "Jump" to original row after quick filter was disabled
        # Jump action includes row selection and blinking animation
        #

        self._logMessagesTable.selectRow(originalRow, ScrollHint.PositionAtCenter)
        self._logMessagesTable.startRowBlinking(originalRow)

    def _jumpBackToFilterView(self):
        self.enableQuickFilter(saveRow=False)
        row = self._filterRowBackup.getValue()
        self._logMessagesTable.selectRow(row)
        self._logMessagesTable.startRowBlinking(row)
        self._logMessagesTable.setFocus()
        self._filterRowBackup.delete()

    def _exitQuickFilter(self):
        if self.quickFilterEnabled():
            self.disableQuickFilter()

        if not self._originalRowBackup.empty():
            row = self._originalRowBackup.getValue()
            self._logMessagesTable.selectRow(row, ScrollHint.PositionAtCenter)
            self._originalRowBackup.delete()

    def _handleJumpBackToFilterView(self):
        if self._canJumpBackToFilterView():
            self._jumpBackToFilterView()
        else:
            self._exitQuickFilter()

    def _canJumpBackToFilterView(self):
        return not self._filterRowBackup.empty()

    #####

    def _tryFocusLogMessagesTableAndGoUp(self):
        self._logMessagesTable.trySetFocusAndGoUp()

    def _tryFocusLogMessagesTableAndGoDown(self):
        self._logMessagesTable.trySetFocusAndGoDown()

    #####

    def uniqueTagNames(self) -> List[str]:
        return self._logMessagesTable.uniqueTagNames()

    #####

    def _contextMenuExec(self, position: QPoint):
        canJumpBack = self._canJumpBackToFilterView()
        self._logMessagesTable.contextMenuExec(position, canJumpBack)

    def _initCustomContextMenu(self):
        self._logMessagesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self._logMessagesTable.customContextMenuRequested.connect(self._contextMenuExec)  # fmt: skip
