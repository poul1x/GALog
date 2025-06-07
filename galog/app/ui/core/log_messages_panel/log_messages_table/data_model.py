from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from typing import Callable, List

from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel, Qt

from galog.app.log_reader import LogLine
from .pattern_search_task import PatternSearchResult


class LazyHighlightingState(int, Enum):
    pending = auto()
    running = auto()
    done = auto()


@dataclass
class HighlightingData:
    state: LazyHighlightingState
    items: List[PatternSearchResult]


class Column(int, Enum):
    tagName = 0
    logLevel = auto()
    logMessage = auto()


class DataModel(QStandardItemModel):
    def __init__(self):
        super().__init__(0, len(Column))
        labels = ["Tag", "Level", "Message"]
        self.setHorizontalHeaderLabels(labels)

    def flags(self, index: QModelIndex):
        default_flags = super().flags(index)
        return default_flags & ~Qt.ItemIsEditable

    def addLogLine(self, logLine: LogLine):
        itemTagName = QStandardItem(logLine.tag)
        itemLogLevel = QStandardItem(logLine.level)
        itemLogMessage = QStandardItem(logLine.msg)

        data = HighlightingData(
            state=LazyHighlightingState.pending,
            items=[],
        )

        # Use this to store data for highlighting
        itemLogMessage.setData(data, Qt.UserRole)

        self.appendRow(
            [
                itemTagName,
                itemLogLevel,
                itemLogMessage,
            ]
        )

    @contextmanager
    def batchInsertMode(self):
        try:
            self.beginResetModel()
            self.blockSignals(True)
            yield

        finally:
            self.blockSignals(False)
            self.endResetModel()

    def clearLogLines(self):
        self.removeRows(0, self.rowCount())

    def logLines(self):
        for row in range(self.rowCount()):
            yield self.logLine(row)

    def logLine(self, row: int):
        return LogLine(
            level=self.item(row, Column.logLevel).text(),
            msg=self.item(row, Column.logMessage).text(),
            tag=self.item(row, Column.tagName).text(),
            pid=-1,
        )

    def logMessage(self, row: int):
        return self.item(row, Column.logMessage).text()

    def uniqueTagNames(self) -> List[str]:
        result = set()
        for i in range(self.rowCount()):
            item = self.item(i, Column.tagName.value)
            result.add(item.text())

        return list(result)
