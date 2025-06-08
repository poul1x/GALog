from typing import List, Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QListView, QWidget

from galog.app.ui.base.list_view import ListView


class FilteredTagsList(ListView):
    selectionChange = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self.setEditTriggers(QListView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.dataModel = QStandardItemModel(self)
        self.setModel(self.dataModel)

        # Make it easier to subscribe for this signal in parent widget
        self.selectionModel().selectionChanged.connect(self.selectionChange.emit)

    def toStringList(self) -> List[str]:
        result = []
        for index in range(self.dataModel.rowCount()):
            item = self.dataModel.item(index)
            result.append(item.text())

        return result

    def hasTag(self, tag: str):
        return bool(self.dataModel.findItems(tag))

    def addTag(self, tag: str):
        self.dataModel.appendRow(QStandardItem(tag))

    def addManyTags(self, tags: List[str]):
        for tag in tags:
            self.dataModel.appendRow(QStandardItem(tag))

    def setTags(self, tags: List[str]):
        self.removeAllTags()
        self.addManyTags(tags)

    def hasTags(self):
        return self.dataModel.rowCount() > 0

    def hasSelectedTags(self):
        return bool(self.selectionModel().selectedRows())

    def removeSelectedTags(self):
        removedRows = []
        for row in self.selectedRows(reverse=True):
            self.dataModel.removeRow(row)
            removedRows.append(row)

        return list(reversed(removedRows))

    def removeAllTags(self):
        self.dataModel.clear()
