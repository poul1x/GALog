from typing import Callable, List, Optional

from galog.app.hrules.hrules import HRulesStorage
from galog.app.log_reader.models import LogLine
from galog.app.ui.base.table_view import TableView, QTableView

from .navigation_frame import NavigationFrame

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtGui import (
    QKeyEvent,
    QResizeEvent,
    QStandardItemModel,
    QFocusEvent,
    QMouseEvent,
    QGuiApplication,
    QFontMetrics,
)
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QTableView,
    QTableWidget,
)

from galog.app.ui.reusable.regexp_filter_model import RegExpFilterModel
from galog.app.ui.reusable.fn_filter_model import FnFilterModel

from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.base.widget import Widget

from .data_model import Column, DataModel
from .navigation_frame import NavigationFrame
from .log_line_delegate import LogLineDelegate
from .vertical_header import VerticalHeader


class LogMessagesTable(TableView):
    requestJumpToOriginalLine = pyqtSignal()
    requestJumpBackToFilterView = pyqtSignal()
    requestShowLineDetails = pyqtSignal()
    requestCopyLogLines = pyqtSignal()
    requestCopyLogMessages = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.XButton1:
            self.requestJumpBackToFilterView.emit()
        elif event.button() == Qt.XButton2:
            self.requestJumpToOriginalLine.emit()
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlEnterPressed():
            self.requestJumpToOriginalLine.emit()
        elif helper.isEnterPressed():
            self.requestShowLineDetails.emit()
        elif helper.isEscapePressed():
            self.requestJumpBackToFilterView.emit()
        elif helper.isCtrlShiftCPressed():
            self.requestCopyLogLines.emit()
        elif helper.isCtrlCPressed():
            self.requestCopyLogMessages.emit()
        else:
            super().keyPressEvent(event)

    def _initLogLineDelegate(self):
        self._delegate = LogLineDelegate(self)
        self.setItemDelegate(self._delegate)

    def setHighlightingRules(self, hrules: HRulesStorage):
        self._delegate.setHighlightingRules(hrules)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initDataModel()
        self._initLogLineDelegate()
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initCustomContextMenu()
        self._scrolling = True

    def _contextMenuExec(self, position: QPoint):
        index = self.indexAt(position)
        if not index.isValid():
            return

        actionView = QAction("View", self)
        actionView.triggered.connect(lambda: self.requestShowLineDetails.emit())

        contextMenu = QMenu(self)
        contextMenu.addAction(actionView)

        if self.quickFilterEnabled():
            actionOrigin = QAction("Go to origin", self)
            actionOrigin.triggered.connect(lambda: self.requestJumpToOriginalLine.emit())
            contextMenu.addAction(actionOrigin)
        else:
            actionBack = QAction("Go back", self)
            actionBack.triggered.connect(lambda: self.requestJumpBackToFilterView.emit())
            contextMenu.addAction(actionBack)

        contextMenu.exec_(self.viewport().mapToGlobal(position))

    def _topModel(self) -> QSortFilterProxyModel:
        return self._quickFilterModel

    def _bottomModel(self) -> QStandardItemModel:
        return self._dataModel

    def _initUserInputHandlers(self):
        self._navigationFrame.upArrowButton.clicked.connect(self._navScrollTop)  # fmt: skip
        self._navigationFrame.downArrowButton.clicked.connect(self._navScrollBottom)  # fmt: skip

    def _initDataModel(self):
        self._dataModel = DataModel()
        self._dataModel.rowsAboutToBeInserted.connect(self._beforeRowInserted)
        self._dataModel.rowsInserted.connect(self._afterRowInserted)

        self._advancedFilterModel = FnFilterModel()
        self._advancedFilterModel.setFilteringColumn(Column.tagName.value)
        self._advancedFilterModel.setSourceModel(self._dataModel)

        self._quickFilterModel = RegExpFilterModel()
        self._quickFilterModel.setFilteringColumn(Column.logMessage.value)
        self._quickFilterModel.setSourceModel(self._advancedFilterModel)
        self.setModel(self._quickFilterModel)

    def _initCustomContextMenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenuExec)

    def _initUserInterface(self):
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.ExtendedSelection)
        self.setCornerButtonEnabled(False)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)

        font = self._delegate.font()
        height = QFontMetrics(font).height()
        height += 5  # vertical padding

        vHeader = VerticalHeader(self)
        vHeader.setVisible(False)
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setMinimumSectionSize(height)
        vHeader.setDefaultSectionSize(height)
        self.setVerticalHeader(vHeader)

        hHeader = self.horizontalHeader()
        hHeader.setSectionResizeMode(Column.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setColumnWidth(Column.logLevel, 10)
        self.setColumnWidth(Column.tagName, 200)

        self._navigationFrame = NavigationFrame(self)
        self._navigationFrame.setMarginTop(hHeader.height() + 10)
        self._navigationFrame.setMarginBottom(10)
        self._navigationFrame.setMarginRight(30)
        self._navigationFrame.setFixedWidth(120)
        self._navigationFrame.updateGeometry()
        self._navigationFrame.hideChildren()

    #####

    def _navScrollTop(self):
        rowCount = self._topModel().rowCount()
        if rowCount > 0:
            self.scrollToTop()
            self.selectRow(0)

    def _navScrollBottom(self):
        rowCount = self._topModel().rowCount()
        if rowCount > 0:
            self.scrollToBottom()
            self.selectRow(rowCount - 1)

    #####

    def _beforeRowInserted(self):
        vbar = self.verticalScrollBar()
        self._scrolling = vbar.value() == vbar.maximum()

    def _afterRowInserted(self):
        if self._scrolling:
            self.scrollToBottom()

    #####

    def resizeEvent(self, e: QResizeEvent):
        self._navigationFrame.updateGeometry()
        return super().resizeEvent(e)

    def setHighlightingEnabled(self, enabled: bool):
        self._delegate.setHighlightingEnabled(enabled)
        self._refreshVisibleIndexes()

    def _refreshVisibleIndexes(self):
        viewportRect = self.viewport().rect()
        topLeft = self.indexAt(viewportRect.topLeft())
        bottomRight = self.indexAt(viewportRect.bottomRight())
        self._topModel().dataChanged.emit(topLeft, bottomRight)

    def setWhiteBackground(self):
        self.setStyleSheet("background: white;")

    #####

    def logLineCount(self):
        return self._dataModel.rowCount()

    def logLine(self, lineNum: int):
        return self._dataModel.logLine(lineNum)

    def logLines(self):
        return self._dataModel.logLines()

    def addLogLine(self, logLine: LogLine):
        self._dataModel.addLogLine(logLine)

    def clearLogLines(self):
        self._dataModel.clearLogLines()

    def enterBatchMode(self):
        return self._dataModel.batchInsertMode()


    #####

    def advancedFilterApply(self, fn: Callable[[str], bool]):
        self._advancedFilterModel.setFilteringFn(fn)

    def advancedFilterReset(self):
        self._advancedFilterModel.setFilteringEnabled(False)

    def advancedFilterEnabled(self):
        self._advancedFilterModel.filteringEnabled()

    #####

    def quickFilterApply(self, column: Column, filterText: str):
        self._quickFilterModel.setFilterKeyColumn(column.value)
        self._quickFilterModel.setFilterFixedString(filterText)
        self.selectRow(0)

    def quickFilterReset(self):
        self._quickFilterModel.setFilterKeyColumn(Column.logMessage.value)
        self._quickFilterModel.setFilterFixedString("")
        self.selectRow(0)

    def quickFilterEnabled(self):
        return self._quickFilterModel.filteringEnabled()

    def setQuickFilterEnabled(self, enabled: bool):
        self.reset()
        self._quickFilterModel.setFilteringEnabled(enabled)
        self._navigationFrame.updateGeometry()

    #####

    def lineNumbersVisible(self):
        self.verticalHeader().isVisible()

    def setLineNumbersVisible(self, visible: bool):
        self.verticalHeader().setVisible(visible)

    #####


    def _dataModelRow(self, row: int):
        index2 = self._quickFilterModel.index(row, 0)
        index1 = self._quickFilterModel.mapToSource(index2)
        index0 = self._advancedFilterModel.mapToSource(index1)
        return index0.row()

    def selectedLogLines(self) -> List[LogLine]:
        result = []
        for row in self.selectedRows():
            realRow = self._dataModelRow(row)
            result.append(self._dataModel.logLine(realRow))

        return result

    def selectedLogMessages(self) -> List[str]:
        result = []
        for row in self.selectedRows():
            realRow = self._dataModelRow(row)
            result.append(self._dataModel.logMessage(realRow))

        return result

    #####

    def resolveOriginalRow(self, filterRow: int):
        index = self._topModel().index(filterRow, 0)
        return self._topModel().mapToSource(index).row()

    def startRowBlinking(self, row: int):
        self._delegate.startRowBlinking(row, self._topModel())

    #####

    def uniqueTagNames(self) -> List[str]:
        return self._dataModel.uniqueTagNames()