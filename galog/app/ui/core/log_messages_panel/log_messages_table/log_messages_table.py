from typing import Optional

from galog.app.hrules.hrules import HRulesStorage

from .navigation_frame import NavigationFrame

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHeaderView,
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

    def topModel(self):
        return self._regExpFilterModel

    def bottomModel(self):
        return self._dataModel

    def _initUserInputHandlers(self):
        self._navigationFrame.upArrowButton.clicked.connect(self._navScrollTop)  # fmt: skip
        self._navigationFrame.downArrowButton.clicked.connect(self._navScrollBottom)  # fmt: skip

    def _initUserInterface(self):
        self._dataModel = DataModel()
        self._dataModel.rowsAboutToBeInserted.connect(self._beforeRowInserted)
        self._dataModel.rowsInserted.connect(self._afterRowInserted)

        self._fnFilterModel = FnFilterModel()
        self._fnFilterModel.setFilteringColumn(Column.tagName.value)
        self._fnFilterModel.setSourceModel(self._dataModel)

        self._regExpFilterModel = RegExpFilterModel()
        self._regExpFilterModel.setFilteringColumn(Column.logMessage.value)
        self._regExpFilterModel.setSourceModel(self._fnFilterModel)

        self._tableView = TableView(self)
        self._tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tableView.customContextMenuRequested.connect(self._contextMenuExec)
        self._tableView.setModel(self._regExpFilterModel)

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

    def _navScrollTop(self):
        rowCount = self.topModel().rowCount()
        if rowCount > 0:
            self._tableView.scrollToTop()
            self._tableView.selectRow(0)

    def _navScrollBottom(self):
        rowCount = self.topModel().rowCount()
        if rowCount > 0:
            self._tableView.scrollToBottom()
            self._tableView.selectRow(rowCount - 1)

    def _beforeRowInserted(self):
        vbar = self._tableView.verticalScrollBar()
        self._scrolling = vbar.value() == vbar.maximum()

    def _afterRowInserted(self):
        if self._scrolling:
            self._tableView.scrollToBottom()

    def resizeEvent(self, e: QResizeEvent):
        self._navigationFrame.updateGeometry()
        return super().resizeEvent(e)

    def setHighlightingRules(self, hrules: HRulesStorage):
        self._tableView.setHighlightingRules(hrules)

    def setHighlightingEnabled(self, enabled: bool):
        self._tableView.setHighlightingEnabled(enabled)
        self._refreshVisibleIndexes()

    def addLogLine(self, tagName: str, logLevel: str, message: str):
        self._dataModel.addLogLine(tagName, logLevel, message)

    def clearLogLines(self):
        self._dataModel.clearLogLines()

    def setWhiteBackground(self):
        self._tableView.setStyleSheet("background: white;")

    def _refreshVisibleIndexes(self):
        viewportRect = self._tableView.viewport().rect()
        topLeft = self._tableView.indexAt(viewportRect.topLeft())
        bottomRight = self._tableView.indexAt(viewportRect.bottomRight())
        self.topModel().dataChanged.emit(topLeft, bottomRight)

