from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex, QDateTime
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
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
    sendTimestamp = 0
    sendDate = 1
    messageBody = 2


class CustomSortProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        filterRegExp = self.filterRegExp()
        if filterRegExp.isEmpty():
            return True

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, Columns.messageBody, sourceParent)
        return filterRegExp.indexIn(sourceModel.data(indexBody)) != -1


class LogMessagesPane(QWidget):

    """Displays log messages"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        labels = ["Log level", "Tag", "Message"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        proxyModel = CustomSortProxyModel()
        proxyModel.setSourceModel(dataModel)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        tableView = QTableView()
        tableView.setModel(proxyModel)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        hHeader = tableView.horizontalHeader()
        # hHeader.setSectionResizeMode(QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.messageBody, QHeaderView.Stretch)
        hHeader.resizeSections(QHeaderView.ResizeToContents)
        # hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(False)

        # searchField = QLineEdit()
        # searchField.setPlaceholderText("Search in message body")
        # searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        # searchField.textChanged.connect(proxyModel.setFilterFixedString)

        layout = QVBoxLayout()
        layout.addWidget(tableView)
        # layout.addWidget(searchField)

        self._tableView = tableView
        self._dataModel = dataModel
        self.setLayout(layout)

    def clear(self):
        self._dataModel.clear()

    def appendRow(self, logLevel, tagName, logMessage):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        itemLogLevel = QStandardItem(logLevel)
        itemLogLevel.setFlags(flags)

        itemTagName = QStandardItem(tagName)
        itemTagName.setFlags(flags)

        itemLogMessage = QStandardItem(logMessage)
        itemLogMessage.setFlags(flags)

        row = [itemLogLevel, itemTagName, itemLogMessage]
        self._dataModel.appendRow(row)
