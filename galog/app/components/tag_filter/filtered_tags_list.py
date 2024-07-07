from typing import List
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPalette, QFont
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListView,
    QAbstractItemView,
    QCompleter,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from galog.app.components.reusable.search_input_auto_complete import (
    SearchInputAutoComplete,
)
from galog.app.util.list_view import ListView


class FilteredTagsList(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)
        vBoxLayout.setContentsMargins(10, 0, 10, 0)
        vBoxLayout.setSpacing(0)

        self.tagListView = ListView(self)
        self.tagListView.setEditTriggers(QListView.NoEditTriggers)
        self.tagListView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.dataModel = QStandardItemModel(self)
        self.tagListView.setModel(self.dataModel)
        vBoxLayout.addWidget(self.tagListView)
        self.setLayout(vBoxLayout)

    def _selectedRows(self):
        selectionModel = self.tagListView.selectionModel()
        return [index.row() for index in selectionModel.selectedRows()]

    def addTag(self, tag: str):
        self.dataModel.appendRow(QStandardItem(tag))

    def addManyTags(self, tags: List[str]):
        for tag in tags:
            self.dataModel.appendRow(QStandardItem(tag))

    def hasTags(self):
        return self.dataModel.rowCount() > 0

    def removeSelectedTags(self):
        selectedRows = self._selectedRows()
        for row in selectedRows:
            self.dataModel.removeRow(row)

        return selectedRows

    def removeAllTags(self):
        self.dataModel.clear()
