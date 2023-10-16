from copy import copy
from random import randint
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum, auto

from PyQt5.QtWidgets import QWidget
from loggat.app.components.message_view_pane import LogMessageViewPane
from loggat.app.highlighting_rules import HighlightingRules

from loggat.app.util.paths import iconFile

from .delegate import HighlightingData, LazyHighlightingState
from .filter_model import FilterModel
from .data_model import DataModel, Columns
from .table_view import TableView


class LogMessagesPane(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.filterModel = FilterModel()
        self.filterModel.setSourceModel(self.dataModel)

        self.tableView = TableView(self)
        self.tableView.setModel(self.filterModel)

        hHeader = self.tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = self.tableView.verticalHeader()
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setDefaultSectionSize(vHeader.minimumSectionSize())
        vHeader.setVisible(False)

        self.searchField = QLineEdit(self)
        self.searchField.setPlaceholderText("Search log message")
        self.searchField.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)

        self.searchButton = QPushButton()
        self.searchButton.setText("Search")

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.searchField)
        hLayout.addWidget(self.searchButton)
        self.searchButton.hide()
        self.searchField.hide()

        vLayout = QVBoxLayout()
        vLayout.addWidget(self.tableView)
        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)

    def clear(self):
        cnt = self.dataModel.rowCount()
        self.dataModel.removeRows(0, cnt)

    def addLogLine(self, logLevel: str, tagName: str, logMessage: str):
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

        self.dataModel.append(itemTagName, itemLogLevel, itemLogMessage)
