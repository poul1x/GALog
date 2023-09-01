from distutils.log import log
from .log_messages_pane import LogMessagesPane
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex, QDateTime
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QLineEdit,
    QWidget,
    QScrollBar,
)


from dataclasses import dataclass
from typing import List
from enum import Enum


class Columns(int, Enum):
    logLevel = 0
    tagName = 1
    logMessage = 2


class CustomSortProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        filterRegExp = self.filterRegExp()
        if filterRegExp.isEmpty():
            return False

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, Columns.logMessage, sourceParent)
        return filterRegExp.indexIn(sourceModel.data(indexBody)) != -1


class SearchPane(QWidget):

    itemDoubleClicked = pyqtSignal(int, int)

    def __init__(self, logMessagesPane: LogMessagesPane, parent: QWidget):
        super().__init__(parent)
        self._logMessagesPane = logMessagesPane
        self.initUserInterface()

    def initUserInterface(self):

        # dataModel = QStandardItemModel(0, len(Columns))
        # dataModel.setHorizontalHeaderLabels(["1", "2", "3"])

        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)


        proxyModel = CustomSortProxyModel()
        proxyModel.setSourceModel(self._logMessagesPane._dataModel)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        tableView = QTableView(self)
        tableView.setModel(proxyModel)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)
        tableView.setColumnWidth(Columns.logLevel, 20)
        tableView.setColumnWidth(Columns.tagName, 200)


        hHeader = tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(True)

        searchField = QLineEdit()
        searchField.setPlaceholderText("Search log message")
        searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        searchField.textChanged.connect(proxyModel.setFilterFixedString)

        layout = QVBoxLayout()
        layout.addWidget(tableView)
        layout.addWidget(searchField)

        tableView.doubleClicked.connect(self.onDoubleClicked)
        self.itemDoubleClicked.connect(self._logMessagesPane.navigateToItem)

        self._tableView = tableView
        self._dataModel = self._logMessagesPane._dataModel
        self._proxyModel = proxyModel
        self.setLayout(layout)

    def onDoubleClicked(self, proxyIndex: QModelIndex):
        index = self._proxyModel.mapToSource(proxyIndex)
        self.itemDoubleClicked.emit(index.row(), index.column())