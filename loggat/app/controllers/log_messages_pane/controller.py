from typing import List
from PyQt5.QtCore import QModelIndex, QThreadPool, Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QTableView, QMessageBox

from loggat.app.components.dialogs import ErrorDialog, LoadingDialog
from loggat.app.components.dialogs.stop_capture_dialog import (
    StopCaptureDialog,
    StopCaptureDialogResult,
)
from loggat.app.components.log_messages_pane.delegate import (
    HighlightingData,
    LazyHighlightingState,
)
from loggat.app.components.log_messages_pane.pane import LogMessagesPane
from loggat.app.components.message_view_pane import LogMessageViewPane
from loggat.app.controllers.kill_app.controller import KillAppController
from loggat.app.controllers.message_view_pane.controller import (
    LogMessageViewPaneController,
)
from loggat.app.controllers.run_app.controller import RunAppController
from loggat.app.device.device import AdbClient

from loggat.app.highlighting_rules import HighlightingRules
from .search import SearchItem, SearchItemTask, SearchResult
from .log_reader import (
    AndroidAppLogReader,
    LogLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)


class LogMessagesPaneController:
    def __init__(self, adbHost: str, adbPort: int):
        self._client = AdbClient(adbHost, adbPort)
        self._viewPaneController = None
        self._highlightingRules = None
        self._logReader = None
        self._liveReload = True
        self._scrolling = True
        self._backToFilter = False

    def setHighlightingRules(self, rules: HighlightingRules):
        self._highlightingRules = rules

    def takeControl(self, pane: LogMessagesPane):
        pane.tableView.activated.connect(self._rowActivated)
        pane.tableView.delegate.setHighlightingRules(self._highlightingRules)
        pane.tableView.delegate.lazyHighlighting.connect(self._lazyHighlighting)
        pane.dataModel.rowsAboutToBeInserted.connect(self._beforeRowInserted)
        pane.dataModel.rowsInserted.connect(self._afterRowInserted)
        pane.searchInput.returnPressed.connect(self._applyMessageFilter)
        pane.searchButton.clicked.connect(self._applyMessageFilter)
        pane.toggleMessageFilter.connect(self._toggleMessageFilter)
        self._pane = pane
        self._scrolling = True
        self._backToFilter = False

        assert self._highlightingRules
        self._viewPaneController = LogMessageViewPaneController(
            pane.dataModel, self._highlightingRules
        )

    def _toggleMessageFilter(self):
        if self.messageFilterEnabled():
            self.disableMessageFilter()
        else:
            if self._backToFilter:
                self.enableMessageFilter(reset=False)
                self._pane.tableView.setFocus()

        self._backToFilter = False

    def setLiveReloadEnabled(self, enabled: bool):
        self._liveReload = enabled

    def _jumpToRow(self, index: QModelIndex):
        dataModelIndex = self._pane.filterModel.mapToSource(index)
        self.disableMessageFilter()
        index = self._pane.filterModel.index(dataModelIndex.row(), 0)
        self._backToFilter = True
        self._pane.tableView.selectRow(index.row())
        flags = QTableView.PositionAtCenter | QTableView.PositionAtTop
        self._pane.tableView.scrollTo(index, flags)

    def _showContentFor(self, index: QModelIndex):
        viewPane = LogMessageViewPane(self._pane)
        self._viewPaneController.takeControl(viewPane)
        self._viewPaneController.showContentFor(index.row())

    def _rowActivated(self, index: QModelIndex):
        if self._pane.filterModel.filteringEnabled():
            self._jumpToRow(index)
        else:
            self._showContentFor(index)

    def _beforeRowInserted(self):
        vbar = self._pane.tableView.verticalScrollBar()
        self._scrolling = vbar.value() == vbar.maximum()

    def _afterRowInserted(self):
        if self._scrolling:
            self._pane.tableView.scrollToBottom()

    def _searchDone(self, index: QModelIndex, results: List[SearchResult]):
        data = HighlightingData(
            state=LazyHighlightingState.done,
            items=results,
        )

        model = index.model()
        model.setData(index, data, Qt.UserRole)
        model.dataChanged.emit(index, index)

    def _lazyHighlighting(self, index: QModelIndex):
        items = []
        for name, pattern in self._highlightingRules.iter():
            items.append(SearchItem(name, pattern))

        task = SearchItemTask(index.data(), items)
        task.signals.finished.connect(lambda results: self._searchDone(index, results))
        QThreadPool.globalInstance().start(task)

    def _lineRead(self, parsedLine: LogLine):
        self._addLogLine(
            parsedLine.level,
            parsedLine.tag,
            parsedLine.msg,
        )

    def _appStarted(self, packageName: str):
        if self._liveReload:
            self._clearLogMessages()
            self.disableMessageFilter()

        msg = f"App '{packageName}' started"
        self._addLogLine("S", "loggat", msg)

    def _processStarted(self, event: ProcessStartedEvent):
        msg = f"Process <PID={event.processId}> started for {event.target}"
        self._addLogLine("S", "loggat", msg)

    def _processEnded(self, event: ProcessEndedEvent):
        msg = f"Process <PID={event.processId}> ended"
        self._addLogLine("S", "loggat", msg)

    def _appEnded(self, packageName: str):
        msg = f"App '{packageName}' ended"
        self._addLogLine("S", "loggat", msg)

    def _promptRunApp(self, deviceName: str, packageName: str):
        buttons = QMessageBox.Yes | QMessageBox.No
        text = "This app is not running. Would you like to start it?"
        reply = QMessageBox.question(None, "Run app", text, buttons)

        if reply == QMessageBox.Yes:
            adbHost = self._client.host
            adbPort = self._client.port
            controller = RunAppController(adbHost, adbPort)
            controller.runApp(deviceName, packageName)

    def _logReaderInitialized(self, deviceName: str, packageName: str, pids: List[str]):
        assert self._loadingDialog
        self._loadingDialog.close()
        self._loadingDialog = None

        if pids:
            msg = f"App '{packageName}' is running. PIDs: {', '.join(pids)}"
            self._addLogLine("S", "loggat", msg)
        else:
            msg = f"App '{packageName}' is not running. Waiting for its start..."
            self._addLogLine("S", "loggat", msg)
            self._promptRunApp(deviceName, packageName)

    def _logReaderFailed(self, msgBrief: str, msgVerbose: str):
        if self._loadingDialog:
            self._loadingDialog.close()
            self._loadingDialog = None

        messageBox = ErrorDialog()
        messageBox.setText(msgBrief)
        messageBox.setInformativeText(msgVerbose)
        messageBox.exec_()

    def startCapture(self, device: str, package: str):
        self._clearLogMessages()
        self._logReader = AndroidAppLogReader(self._client, device, package)
        self._logReader.signals.failed.connect(self._logReaderFailed)
        self._logReader.signals.initialized.connect(self._logReaderInitialized)
        self._logReader.signals.appStarted.connect(self._appStarted)
        self._logReader.signals.appEnded.connect(self._appEnded)
        self._logReader.signals.processStarted.connect(self._processStarted)
        self._logReader.signals.processEnded.connect(self._processEnded)
        self._logReader.signals.lineRead.connect(self._lineRead)
        self._logReader.setStartDelay(750)
        self._logReader.start()

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Connecting to ADB server...")
        self._loadingDialog.exec_()

    def promptStopCapture(self):
        dialog = StopCaptureDialog()
        dialog.setText("Stop capture?")

        result = dialog.exec_()
        if result == StopCaptureDialogResult.Rejected:
            return False

        assert self._client is not None
        assert self._logReader is not None
        if result == StopCaptureDialogResult.AcceptedKillApp:
            adbHost = self._client.host
            adbPort = self._client.port
            device = self._logReader.device
            package = self._logReader.package
            controller = KillAppController(adbHost, adbPort)
            controller.killApp(device, package)

        self.stopCapture()
        return True

    def stopCapture(self):
        if self._logReader:
            self._logReader.stop()
            self._logReader = None

    def _applyMessageFilter(self):
        text = self._pane.searchInput.text()
        self._pane.filterModel.setFilterFixedString(text)

    def _resetMessageFilter(self):
        self._pane.searchInput.setText("")
        self._pane.filterModel.setFilterFixedString("")

    def enableMessageFilter(self, reset: bool = True):
        self._pane.filterModel.setFilteringEnabled(True)
        self._pane.tableView.verticalHeader().setVisible(True)
        self._pane.searchInput.setFocusPolicy(Qt.TabFocus)
        self._pane.searchInput.setFocus()
        self._pane.searchButton.show()
        self._pane.searchInput.show()

        if reset == True:
            self._resetMessageFilter()

    def disableMessageFilter(self):
        self._pane.filterModel.setFilteringEnabled(False)
        self._pane.tableView.verticalHeader().setVisible(False)
        self._pane.tableView.reset()
        self._pane.searchInput.setFocusPolicy(Qt.NoFocus)
        self._pane.searchInput.hide()
        self._pane.searchButton.hide()

    def messageFilterEnabled(self):
        return self._pane.filterModel.filteringEnabled()

    def _clearLogMessages(self):
        cnt = self._pane.dataModel.rowCount()
        self._pane.dataModel.removeRows(0, cnt)

    def _addLogLine(self, logLevel: str, tagName: str, logMessage: str):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        itemLogLevel = QStandardItem(logLevel)
        itemLogLevel.setFlags(flags)

        itemTagName = QStandardItem(tagName)
        itemTagName.setFlags(flags)

        data = HighlightingData(
            state=LazyHighlightingState.pending,
            items=[],
        )

        itemLogMessage = QStandardItem(logMessage)
        itemLogMessage.setData(data, Qt.UserRole)
        itemLogMessage.setFlags(flags)

        self._pane.dataModel.append(
            itemTagName,
            itemLogLevel,
            itemLogMessage,
        )
