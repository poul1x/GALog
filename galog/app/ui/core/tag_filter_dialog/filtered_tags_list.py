from typing import List

from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal, QItemSelectionModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QListView, QVBoxLayout, QWidget

from galog.app.ui.base.list_view import ListView
from galog.app.ui.base.widget import Widget


class FilteredTagsList(Widget):
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
        for row in self.listView.selectedRows():
            self.dataModel.removeRow(row)
            removedRows.append(row)

        return removedRows

    def selectTagByRow(self, row: int):
        return self.listView.selectRow(row)

    def removeAllTags(self):
        self.dataModel.clear()

    def trySetFocusAndGoUp(self):
        return self.listView.trySetFocusAndGoUp()

    def trySetFocusAndGoDown(self):
        return self.listView.trySetFocusAndGoDown()