from dataclasses import dataclass
from enum import Enum, auto

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from typing import Callable, List

from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel, Qt
from .pattern_search_task import SearchResult


class LazyHighlightingState(int, Enum):
    pending = auto()
    running = auto()
    done = auto()


@dataclass
class HighlightingData:
    state: LazyHighlightingState
    items: List[SearchResult]


class Column(int, Enum):
    tagName = 0
    logLevel = auto()
    logMessage = auto()


class DataModel(QStandardItemModel):
    def __init__(self):
        super().__init__(0, len(Column))
        labels = ["Tag", "Level", "Message"]
        self.setHorizontalHeaderLabels(labels)

    def addLogLine(
        self,
        tagName: str,
        logLevel: str,
        message: str,
    ):
        # flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        itemLogLevel = QStandardItem(logLevel)
        itemLogLevel.setData(False, Qt.UserRole)  # is row color inverted
        # itemLogLevel.setFlags(flags)

        itemTagName = QStandardItem(tagName)
        # itemTagName.setFlags(flags)

        data = HighlightingData(
            state=LazyHighlightingState.pending,
            items=[],
        )

        itemLogMessage = QStandardItem(message)
        itemLogMessage.setData(data, Qt.UserRole)
        # itemLogMessage.setFlags(flags)

        self.appendRow(
            [
                itemTagName,
                itemLogLevel,
                itemLogMessage,
            ]
        )

    def clearLogLines(self):
        self.removeRows(0, self.rowCount())
