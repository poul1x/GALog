from typing import List
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal
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
    QSizePolicy,
    QFrame,
)
from galog.app.components.reusable.search_input_auto_complete import (
    SearchInputAutoComplete,
)
from galog.app.util.list_view import ListView


class FilteredTagsList(QWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
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
        return [(index.row(), index.data()) for index in selectedRows]

    def addTag(self, tag: str):
        self.dataModel.appendRow(QStandardItem(tag))

    def addManyTags(self, tags: List[str]):
        for tag in tags:
            self.dataModel.appendRow(QStandardItem(tag))

    def hasTags(self):
        return self.dataModel.rowCount() > 0

    def hasSelectedTags(self):
        return bool(self.tagListView.selectionModel().selectedRows())

    def removeSelectedTags(self):
        result = []
        for row, tag in self._selectedRows():
            self.dataModel.removeRow(row)
            result.append(tag)

        return result

    def removeAllTags(self):
        self.dataModel.clear()
