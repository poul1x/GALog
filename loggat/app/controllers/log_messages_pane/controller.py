from typing import List
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from loggat.app.components.dialogs import ErrorDialog, LoadingDialog
from loggat.app.components.log_messages_pane.delegate import (
    HighlightingData,
    LazyHighlightingState,
)
from loggat.app.components.log_messages_pane.pane import LogMessagesPane
from loggat.app.components.message_view_pane import LogMessageViewPane
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
        self._liveReload = True
        self._scrolling = True

    def setHighlightingRules(self, rules: HighlightingRules):
        self._highlightingRules = rules

    def takeControl(self, pane: LogMessagesPane):
        pane.tableView.activated.connect(self.rowActivated)
        pane.tableView.delegate.setHighlightingRules(self._highlightingRules)
        pane.tableView.delegate.lazyHighlighting.connect(self.lazyHighlighting)
        pane.dataModel.rowsAboutToBeInserted.connect(self.beforeRowInserted)
        pane.dataModel.rowsInserted.connect(self.afterRowInserted)
        pane.searchField.returnPressed.connect(self.applyFilter)
        pane.searchButton.clicked.connect(self.applyFilter)
        self._pane = pane
        self._scrolling = True

        assert self._highlightingRules
        self._viewPaneController = LogMessageViewPaneController(
            pane.dataModel, self._highlightingRules
        )

    def setLiveReloadEnabled(self, enabled: bool):
        self._liveReload = enabled

    # TODO: inspect this function
    def rowActivated(self, index: QModelIndex):
        if self._pane.filterModel.filteringEnabled():
            dataModelIndex = self._pane.filterModel.mapToSource(index)
            self.disableFilter()

            # self._pane.tableView.
            self._pane.tableView.reset()  # ? disableFilter
            # self._pane.tableView.scrollToBottom()
            index = self._pane.filterModel.index(dataModelIndex.row(), 0)
            self._pane.tableView.scrollTo(index, QTableView.PositionAtCenter)
        else:
            viewPane = LogMessageViewPane(self._pane)
            self._viewPaneController.takeControl(viewPane)
            self._viewPaneController.showContentFor(index.row())

    def beforeRowInserted(self):
        vbar = self._pane.tableView.verticalScrollBar()
        self._scrolling = vbar.value() == vbar.maximum()

    def afterRowInserted(self):
        if self._scrolling:
            self._pane.tableView.scrollToBottom()

    def enableFilter(self):
        self._pane.filterModel.setFilteringEnabled(True)
        self._pane.tableView.verticalHeader().setVisible(True)
        self._pane.searchField.setFocus()
        self._pane.searchButton.show()
        self._pane.searchField.show()

    def disableFilter(self):
        self._pane.filterModel.setFilteringEnabled(False)
        self._pane.tableView.verticalHeader().setVisible(False)
        self._pane.searchButton.hide()
        self._pane.searchField.hide()

    def applyFilter(self):
        text = self._pane.searchField.text()
        self._pane.filterModel.setFilterFixedString(text)

    def searchDone(self, index: QModelIndex, results: List[SearchResult]):
        data = HighlightingData(
            state=LazyHighlightingState.done,
            items=results,
        )

        model = index.model()
        model.setData(index, data, Qt.UserRole)
        model.dataChanged.emit(index, index)

    def lazyHighlighting(self, index: QModelIndex):
        items = []
        for name, pattern in self._highlightingRules.iter():
            items.append(SearchItem(name, pattern))

        task = SearchItemTask(index.data(), items)
        task.signals.finished.connect(lambda results: self.searchDone(index, results))
        QThreadPool.globalInstance().start(task)

    def lineRead(self, parsedLine: LogLine):
        self._pane.addLogLine(
            parsedLine.level,
            parsedLine.tag,
            parsedLine.msg,
        )

    def appStarted(self, packageName: str):
        if self._liveReload:
            self._pane.clear()
            self.disableFilter()

        msg = f"App '{packageName}' started"
        self._pane.addLogLine("S", "loggat", msg)

    def processStarted(self, event: ProcessStartedEvent):
        msg = f"Process <PID={event.processId}> started for {event.target}"
        self._pane.addLogLine("S", "loggat", msg)

    def processEnded(self, event: ProcessEndedEvent):
        msg = f"Process <PID={event.processId}> ended"
        self._pane.addLogLine("S", "loggat", msg)

    def appEnded(self, packageName: str):
        msg = f"App '{packageName}' ended"
        self._pane.addLogLine("S", "loggat", msg)

    def _promptRunApp(self, deviceName: str, packageName: str):
        buttons = QMessageBox.Yes | QMessageBox.No
        text = "This app is not running. Would you like to start it?"
        reply = QMessageBox.question(None, "Run app", text, buttons)

        if reply == QMessageBox.Yes:
            adbHost = self._client.host
            adbPort = self._client.port
            controller = RunAppController(adbHost, adbPort)
            controller.runApp(deviceName, packageName)

    def logReaderInitialized(self, deviceName: str, packageName: str, pids: List[str]):
        assert self._loadingDialog
        self._loadingDialog.close()
        self._loadingDialog = None

        if pids:
            msg = f"App '{packageName}' is running. PIDs: {', '.join(pids)}"
            self._pane.addLogLine("S", "loggat", msg)
        else:
            self._promptRunApp(deviceName, packageName)

    def logReaderFailed(self, msgBrief: str, msgVerbose: str):
        if self._loadingDialog:
            self._loadingDialog.close()
            self._loadingDialog = None

        messageBox = ErrorDialog()
        messageBox.setText(msgBrief)
        messageBox.setInformativeText(msgVerbose)
        messageBox.exec_()

    def startCapture(self, device: str, package: str):
        self._pane.clear()
        self._logReader = AndroidAppLogReader(self._client, device, package)
        self._logReader.signals.failed.connect(self.logReaderFailed)
        self._logReader.signals.initialized.connect(self.logReaderInitialized)
        self._logReader.signals.appStarted.connect(self.appStarted)
        self._logReader.signals.appEnded.connect(self.appEnded)
        self._logReader.signals.processStarted.connect(self.processStarted)
        self._logReader.signals.processEnded.connect(self.processEnded)
        self._logReader.signals.lineRead.connect(self.lineRead)
        QTimer.singleShot(750, lambda: self._logReader.start())

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Connecting to ADB server...")
        self._loadingDialog.exec_()

    def stopCapture(self):
        self._logReader.stop()
        self._logReader = None
