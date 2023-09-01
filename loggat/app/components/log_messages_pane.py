from traceback import print_tb
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum


class Columns(int, Enum):
    logLevel = 0
    tagName = 1
    logMessage = 2


class LogMessagesPane(QWidget):

    """Displays log messages"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):

        labels = ["Log level", "Tag", "Message"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        tableView = QTableView(self)
        tableView.setModel(dataModel)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)
        tableView.setColumnWidth(Columns.logLevel, 20)
        tableView.setColumnWidth(Columns.tagName, 200)

        hHeader = tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(tableView)

        self._tableView = tableView
        self._dataModel = dataModel
        self.setLayout(layout)

        self._scroll = True
        self._dataModel.rowsAboutToBeInserted.connect(self.beforeInsert)
        self._dataModel.rowsInserted.connect(self.afterInsert)

    def beforeInsert(self):
        vbar = self._tableView.verticalScrollBar()
        self._scroll = vbar.value() == vbar.maximum()

    def afterInsert(self):
        if self._scroll:
            self._tableView.scrollToBottom()

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

    def navigateToItem(self, row, col):
        self.activateWindow()
        self.raise_()
        if 0 <= row < self._dataModel.rowCount() and 0 <= col < self._dataModel.columnCount():
            self._tableView.selectRow(row)