from typing import List

from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal, QItemSelectionModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QListView, QVBoxLayout, QWidget

from galog.app.ui.base.list_view import ListView
from galog.app.ui.base.widget import BaseWidget


class FilteredTagsList(BaseWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)

        self.listView = ListView(self)
        self.listView.setEditTriggers(QListView.NoEditTriggers)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.dataModel = QStandardItemModel(self)
        self.listView.setModel(self.dataModel)
        vBoxLayout.addWidget(self.listView)
        self.setLayout(vBoxLayout)

        # Make it easier to subscribe for this signal in parent widget
        self.listView.selectionModel().selectionChanged.connect(
            self.selectionChanged.emit
        )

    def _selectedRows(self):
        def key(index: QModelIndex):
            return index.row()

        selectionModel = self.listView.selectionModel()
        selectedRows = sorted(selectionModel.selectedRows(), key=key, reverse=True)
        return [index.row() for index in selectedRows]

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
        return bool(self.listView.selectionModel().selectedRows())

    def removeSelectedTags(self):
        removedRows = []
        for row in self._selectedRows():
            self.dataModel.removeRow(row)
            removedRows.append(row)

        return removedRows

    def selectRow(self, row: int):
        if row < 0 or row >= self.dataModel.rowCount():
            return False

        index = self.dataModel.index(row, 0)
        self.selectRowByIndex(index)
        return True

    def selectRowByIndex(self, index: QModelIndex):
        assert index.isValid(), "Index must be valid"
        self.listView.setCurrentIndex(index)
        selectionModel = self.listView.selectionModel()
        selectionModel.select(index, QItemSelectionModel.Select)
        self.listView.scrollTo(index, QListView.PositionAtCenter)

    def removeAllTags(self):
        self.dataModel.clear()
