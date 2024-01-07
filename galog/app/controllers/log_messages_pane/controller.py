from typing import TYPE_CHECKING, List

from PyQt5.QtCore import QModelIndex, Qt, QThread, QThreadPool
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QTableView

from galog.app.components.dialogs import LoadingDialog
from galog.app.components.log_messages_pane.data_model import Columns
from galog.app.components.log_messages_pane.delegate import (
    HighlightingData,
    LazyHighlightingState,
)
from galog.app.components.log_messages_pane.pane import LogMessagesPane
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.controllers.message_view_pane.controller import (
    LogMessageViewPaneController,
)
from galog.app.device.device import AdbClient
from galog.app.highlighting import HighlightingRules
from galog.app.util.message_box import showErrorMsgBox

from .blinking_row import RowBlinkingController
from .log_reader import (
    AndroidAppLogReader,
    LogLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)
from .search import SearchItem, SearchItemTask, SearchResult

if TYPE_CHECKING:
    from galog.app.main import MainWindow
else:
    MainWindow = object


class LogMessagesPaneController:
    def __init__(self, mainWindow: MainWindow):
        self._client = AdbClient()
        self._mainWindow = mainWindow
        self._rowBlinkingController = None
        self._viewPaneController = None
        self._highlightingRules = None
        self._logReader = None
        self._liveReload = True
        self._lineNumbersVisible = False
        self._scrolling = True
        self._backToFilter = None

    @property
    def device(self):
        assert self._logReader is not None
        return self._logReader.device

    @property
    def package(self):
        assert self._logReader is not None
        return self._logReader.package

    def setHighlightingRules(self, rules: HighlightingRules):
        self._highlightingRules = rules

    def takeControl(self, pane: LogMessagesPane):
        pane.tableView.rowActivated.connect(self._rowActivated)
        pane.tableView.delegate.setHighlightingRules(self._highlightingRules)
        pane.tableView.delegate.lazyHighlighting.connect(self._lazyHighlighting)
        pane.dataModel.rowsAboutToBeInserted.connect(self._beforeRowInserted)
        pane.dataModel.rowsInserted.connect(self._afterRowInserted)
        pane.searchPane.input.returnPressed.connect(self._applyMessageFilter)
        pane.searchPane.button.clicked.connect(self._applyMessageFilter)
        pane.toggleMessageFilter.connect(self._toggleMessageFilter)
        self._pane = pane
        self._scrolling = True
        self._backToFilter = None

        assert self._highlightingRules is not None
        self._viewPaneController = LogMessageViewPaneController(
            pane.dataModel, self._highlightingRules
        )

        self._rowBlinkingController = RowBlinkingController(self._pane)

    def _toggleMessageFilter(self):
        if self.messageFilterEnabled():
            self.disableMessageFilter()
        else:
            if self._backToFilter is not None:
                self._jumpBack()

    def setLiveReloadEnabled(self, enabled: bool):
        self._liveReload = enabled

    def _showLineNumbers(self):
        self._pane.tableView.verticalHeader().setVisible(True)

    def _hideLineNumbers(self):
        if self._lineNumbersVisible:
            return

        self._pane.tableView.verticalHeader().setVisible(False)

    def setShowLineNumbers(self, enabled: bool):
        self._lineNumbersVisible = enabled
        if self.messageFilterEnabled():
            return

        if self._lineNumbersVisible:
            self._showLineNumbers()
        else:
            self._hideLineNumbers()

    def _blinkRow(self):
        model = self._pane.tableView.model()
        for _ in range(10):
            for column in Columns:
                index = model.index(0, column)
                color1 = model.data(index, Qt.TextColorRole)
                color2 = model.data(index, Qt.BackgroundRole)
                model.setData(index, color1, Qt.BackgroundRole)
                model.setData(index, color2, Qt.TextColorRole)
            QThread.msleep(500)

    def _jumpBack(self):
        self.enableMessageFilter(reset=False)
        index = self._pane.filterModel.index(self._backToFilter, 0)
        self._backToFilter = None
        self._pane.tableView.selectRow(index.row())
        flags = QTableView.PositionAtCenter | QTableView.PositionAtTop
        self._pane.tableView.scrollTo(index, flags)
        self._pane.tableView.setFocus()
        self._rowBlinkingController.startBlinking(index.row())

    def _jumpToRow(self, index: QModelIndex):
        self._backToFilter = index.row()
        dataModelIndex = self._pane.filterModel.mapToSource(index)
        self.disableMessageFilter()
        index = self._pane.filterModel.index(dataModelIndex.row(), 0)
        self._pane.tableView.selectRow(index.row())
        flags = QTableView.PositionAtCenter | QTableView.PositionAtTop
        self._pane.tableView.scrollTo(index, flags)
        self._rowBlinkingController.startBlinking(index.row())

    def _showContentFor(self, index: QModelIndex):
        viewPane = LogMessageViewPane(self._pane)
        self._viewPaneController.takeControl(viewPane)
        highlightingEnabled = self._pane.tableView.delegate.highlightingEnabled()
        self._viewPaneController.showContentFor(index.row(), highlightingEnabled)

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
        for name, rule in self._highlightingRules.items():
            groups = set()
            if rule.match:
                groups.add(0)
            if rule.groups:
                groups.update(rule.groups.keys())

            item = SearchItem(name, rule.pattern, rule.priority, groups)
            items.append(item)

        task = SearchItemTask(index.data(), items)
        task.signals.finished.connect(lambda results: self._searchDone(index, results))
        QThreadPool.globalInstance().start(task)

    def addLogLine(self, line: LogLine):
        self._addLogLine(line.level, line.tag, line.msg)

    def _lineRead(self, parsedLine: LogLine):
        self.addLogLine(parsedLine)

    def _appStarted(self, packageName: str):
        if self._liveReload:
            self.clearLogLines()
            self.disableMessageFilter()

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

    def _logReaderInitialized(self, deviceName: str, packageName: str, pids: List[str]):
        assert self._loadingDialog
        self._loadingDialog.close()
        self._loadingDialog = None

        if pids:
            msg = f"App '{packageName}' is running. PID(s): {', '.join(pids)}"
            self._addLogLine("S", "galog", msg)
        else:
            msg = f"App '{packageName}' is not running. Waiting for its start..."
            self._addLogLine("S", "galog", msg)

    def _logReaderFailed(self, msgBrief: str, msgVerbose: str):
        if self._loadingDialog:
            self._loadingDialog.close()
            self._loadingDialog = None

        self._mainWindow.setCaptureSpecificActionsEnabled(False)
        showErrorMsgBox(msgBrief, msgVerbose)

    def makeWhiteBackground(self):
        self._pane.tableView.setStyleSheet("background: white;")

    def startCapture(self, device: str, package: str):
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
        self._loadingDialog.setText(f"Fetching app logs...")
        self._loadingDialog.exec_()

    def stopCapture(self):
        if self._logReader:
            self._logReader.stop()
            self._logReader = None

    def isCaptureRunning(self):
        return self._logReader and self._logReader.isRunning()

    def _applyMessageFilter(self):
        text = self._pane.searchPane.input.text()
        self._pane.filterModel.setFilterFixedString(text)
        if self._pane.filterModel.rowCount() > 0:
            self._pane.tableView.selectRow(0)

    def _resetMessageFilter(self):
        self._pane.searchPane.input.setText("")
        self._pane.filterModel.setFilterFixedString("")

    def enableMessageFilter(self, reset: bool = True):
        self._showLineNumbers()
        self._pane.filterModel.setFilteringEnabled(True)
        self._pane.searchPane.input.setFocusPolicy(Qt.TabFocus)
        self._pane.searchPane.input.setFocus()
        self._pane.searchPane.show()

        if reset == True:
            self._resetMessageFilter()

    def disableMessageFilter(self):
        self._hideLineNumbers()
        self._pane.filterModel.setFilteringEnabled(False)
        self._pane.tableView.reset()
        self._pane.searchPane.input.setFocusPolicy(Qt.NoFocus)
        self._pane.searchPane.hide()

    def messageFilterEnabled(self):
        return self._pane.filterModel.filteringEnabled()

    def clearLogLines(self):
        cnt = self._pane.dataModel.rowCount()
        self._pane.dataModel.removeRows(0, cnt)

    def _addLogLine(self, logLevel: str, tagName: str, logMessage: str):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        itemLogLevel = QStandardItem(logLevel)
        itemLogLevel.setData(False, Qt.UserRole)  # is row color inverted
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

    def _refreshVisibleIndexes(self):
        viewportRect = self._pane.tableView.viewport().rect()
        topLeft = self._pane.tableView.indexAt(viewportRect.topLeft())
        bottomRight = self._pane.tableView.indexAt(viewportRect.bottomRight())
        self._pane.filterModel.dataChanged.emit(topLeft, bottomRight)

    def setHighlightingEnabled(self, enabled: bool):
        self._pane.tableView.delegate.setHighlightingEnabled(enabled)
        self._refreshVisibleIndexes()

    def logLines(self):
        model = self._pane.dataModel

        def logLine(i: int):
            return LogLine(
                level=model.item(i, Columns.logLevel).text(),
                msg=model.item(i, Columns.logMessage).text(),
                tag=model.item(i, Columns.tagName).text(),
                pid=-1,
            )

        return [logLine(i) for i in range(model.rowCount())]

    def addLogLines(self, lines: List[LogLine]):
        for line in lines:
            self.addLogLine(line)
