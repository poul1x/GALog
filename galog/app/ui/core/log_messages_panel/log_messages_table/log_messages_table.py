from typing import Callable, List, Optional

from galog.app.hrules.hrules import HRulesStorage
from galog.app.log_reader.models import LogLine

from .navigation_frame import NavigationFrame

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtGui import QKeyEvent, QResizeEvent, QStandardItemModel, QFocusEvent, QMouseEvent
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QTableView
)

from galog.app.ui.reusable import SearchInput
from galog.app.ui.reusable import RegExpFilterModel
from galog.app.ui.reusable import FnFilterModel

from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.base.widget import BaseWidget

from .table_view import TableView

from .data_model import Column, DataModel
from .navigation_frame import NavigationFrame


class LogMessagesTable(BaseWidget):
    copyMsgRowsToClipboard = pyqtSignal()
    copyFullRowsToClipboard = pyqtSignal()
    cmViewMessage = pyqtSignal(QModelIndex)
    cmGoToOrigin = pyqtSignal(QModelIndex)
    cmGoBack = pyqtSignal()

    rowGoToOrigin = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initUserInterface()
        self._initUserInputHandlers()
        self._scrolling = True

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlEnterPressed():
            self.rowGoToOrigin.emit()
        elif helper.isCtrlShiftCPressed():
            self.copyFullRowsToClipboard.emit()
        elif helper.isCtrlCPressed():
            self.copyMsgRowsToClipboard.emit()
        else:
            super().keyPressEvent(event)

    def _contextMenuExec(self, position: QPoint):
        index = self._tableView.indexAt(position)
        if not index.isValid():
            return

        contextMenu = QMenu(self)
        actionView = QAction("View", self)
        actionOrigin = QAction("Go to origin", self)
        actionBack = QAction("Go back", self)
        actionView.triggered.connect(lambda: self.cmViewMessage.emit(index))
        actionOrigin.triggered.connect(lambda: self.cmGoToOrigin.emit(index))
        actionBack.triggered.connect(lambda: self.cmGoBack.emit())

        contextMenu.addAction(actionView)
        contextMenu.addAction(actionOrigin)
        contextMenu.addAction(actionBack)

        viewport = self._tableView.viewport()
        contextMenu.exec_(viewport.mapToGlobal(position))

    def _topModel(self) -> QSortFilterProxyModel:
        return self._quickFilterModel

    def _bottomModel(self) -> DataModel:
        return self._dataModel

    def _initUserInputHandlers(self):
        self._navigationFrame.upArrowButton.clicked.connect(self._navScrollTop)  # fmt: skip
        self._navigationFrame.downArrowButton.clicked.connect(self._navScrollBottom)  # fmt: skip


    def _initUserInterface(self):
        self._dataModel = DataModel()
        self._dataModel.rowsAboutToBeInserted.connect(self._beforeRowInserted)
        self._dataModel.rowsInserted.connect(self._afterRowInserted)

        self._advancedFilterModel = FnFilterModel()
        self._advancedFilterModel.setFilteringColumn(Column.tagName.value)
        self._advancedFilterModel.setSourceModel(self._dataModel)

        self._quickFilterModel = RegExpFilterModel()
        self._quickFilterModel.setFilteringColumn(Column.logMessage.value)
        self._quickFilterModel.setSourceModel(self._advancedFilterModel)

        self._tableView = TableView(self)
        self._tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tableView.customContextMenuRequested.connect(self._contextMenuExec)
        self._tableView.setSelectionMode(QTableView.ExtendedSelection)
        self._tableView.setModel(self._quickFilterModel)
        self.setFocusProxy(self._tableView)

        hHeader = self._tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Column.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._tableView.setColumnWidth(Column.logLevel, 10)
        self._tableView.setColumnWidth(Column.tagName, 200)

        self._navigationFrame = NavigationFrame(self)
        height = self._tableView.horizontalHeader().height()
        self._navigationFrame.setMarginTop(height + 10)
        self._navigationFrame.setMarginBottom(10)
        self._navigationFrame.setMarginRight(30)
        self._navigationFrame.setFixedWidth(120)
        self._navigationFrame.updateGeometry()
        self._navigationFrame.hideChildren()

        layout = QHBoxLayout()
        layout.addWidget(self._tableView)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    #####

    def _navScrollTop(self):
        rowCount = self._topModel().rowCount()
        if rowCount > 0:
            self._tableView.scrollToTop()
            self._tableView.selectRow(0)

    def _navScrollBottom(self):
        rowCount = self._topModel().rowCount()
        if rowCount > 0:
            self._tableView.scrollToBottom()
            self._tableView.selectRow(rowCount - 1)

    #####

    def _beforeRowInserted(self):
        vbar = self._tableView.verticalScrollBar()
        self._scrolling = vbar.value() == vbar.maximum()

    def _afterRowInserted(self):
        if self._scrolling:
            self._tableView.scrollToBottom()

    #####

    def resizeEvent(self, e: QResizeEvent):
        self._navigationFrame.updateGeometry()
        return super().resizeEvent(e)

    def setHighlightingRules(self, hrules: HRulesStorage):
        self._tableView.setHighlightingRules(hrules)

    def setHighlightingEnabled(self, enabled: bool):
        self._tableView.setHighlightingEnabled(enabled)
        self._refreshVisibleIndexes()

    def _refreshVisibleIndexes(self):
        viewportRect = self._tableView.viewport().rect()
        topLeft = self._tableView.indexAt(viewportRect.topLeft())
        bottomRight = self._tableView.indexAt(viewportRect.bottomRight())
        self._topModel().dataChanged.emit(topLeft, bottomRight)

    def setWhiteBackground(self):
        self._tableView.setStyleSheet("background: white;")

    #####

    def addLogLine(self, logLine: LogLine):
        self._dataModel.addLogLine(logLine)

    def clearLogLines(self):
        self._dataModel.clearLogLines()

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
        self._tableView.selectRow(0)

    def quickFilterReset(self):
        self._quickFilterModel.setFilterKeyColumn(Column.logMessage.value)
        self._quickFilterModel.setFilterFixedString("")
        self._tableView.selectRow(0)

    def quickFilterEnabled(self):
        return self._quickFilterModel.filteringEnabled()

    def setQuickFilterEnabled(self, enabled: bool):
        self._tableView.reset()
        self._quickFilterModel.setFilteringEnabled(enabled)
        self._navigationFrame.updateGeometry()

    #####

    def lineNumbersVisible(self):
        self._tableView.verticalHeader().isVisible()

    def setLineNumbersVisible(self, visible: bool):
        self._tableView.verticalHeader().setVisible(visible)

    #####


    def selectedLogLines(self) -> List[LogLine]:
        result = []
        for row in sorted(self._tableView.selectedRows()):
            result.append(self._bottomModel().logLine(row))

        return result

    def selectedLogMessages(self) -> List[str]:
        result = []
        for row in sorted(self._tableView.selectedRows()):
            result.append(self._bottomModel().logMessage(row))

        return result


