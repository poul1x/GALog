from PyQt5.QtGui import QStandardItem, QStandardItemModel

from enum import Enum, auto


class Columns(int, Enum):
    tagName = 0
    logLevel = auto()
    logMessage = auto()


class DataModel(QStandardItemModel):
    def __init__(self):
        super().__init__(0, len(Columns))
        labels = ["Tag", "Log level", "Message"]
        self.setHorizontalHeaderLabels(labels)

    def append(
        self,
        itemTagName: QStandardItem,
        itemLogLevel: QStandardItem,
        itemLogMessage: QStandardItem,
    ):
        row = [itemTagName, itemLogLevel, itemLogMessage]
        self.appendRow(row)
