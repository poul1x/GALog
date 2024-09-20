from typing import List

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QListView, QVBoxLayout, QWidget

from galog.app.util.list_view import ListView


class FilteredTagsList(QWidget):
    selectionChanged = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)

        self.tagListView = ListView(self)
        self.tagListView.setEditTriggers(QListView.NoEditTriggers)
        self.tagListView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.dataModel = QStandardItemModel(self)
        self.tagListView.setModel(self.dataModel)
        vBoxLayout.addWidget(self.tagListView)
        self.setLayout(vBoxLayout)

        self.tagListView.selectionModel().selectionChanged.connect(
            self._onSelectionChanged
        )

    def _onSelectionChanged(self, *unused):
        self.selectionChanged.emit()

    def _selectedRows(self):
        def key(index: QModelIndex):
            return index.row()

        selectionModel = self.tagListView.selectionModel()
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
        return bool(self.tagListView.selectionModel().selectedRows())

    def removeSelectedTags(self):
        for row in self._selectedRows():
            self.dataModel.removeRow(row)

    def removeAllTags(self):
        self.dataModel.clear()
