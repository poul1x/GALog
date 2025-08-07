from typing import Optional

from PyQt5.QtCore import (
    QItemSelectionModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView, QVBoxLayout, QWidget

from galog.app.ui.base.list_view import ListView
from galog.app.ui.base.widget import Widget
from galog.app.ui.reusable.search_input import SearchInput


class FontList(Widget):

    currentFontChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._initUserInterface()
        self._initUserInputHandlers()

    def _currentFontChanged(self, current: QModelIndex, previous: QModelIndex):
        if not current.isValid():
            return

        fontFamily = self.filterModel.data(current)
        self.currentFontChanged.emit(fontFamily)

    def _initUserInputHandlers(self):
        selectionModel = self.listView.selectionModel()
        selectionModel.currentChanged.connect(self._currentFontChanged)

    def _initUserInterface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.listView = ListView(self)
        self.listView.setEditTriggers(QListView.NoEditTriggers)

        self.dataModel = QStandardItemModel(self)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)
        self.listView.setModel(self.filterModel)
        layout.addWidget(self.listView)

        self.searchInput = SearchInput(self)
        self.searchInput.setPlaceholderText("Search font")
        self.searchInput.textChanged.connect(self._onSearchContentChanged)
        layout.addWidget(self.searchInput)

        self.setLayout(layout)

    def addFont(self, fontName: str):
        self.dataModel.appendRow(QStandardItem(fontName))

    def _removeAllFonts(self):
        rowCount = self.dataModel.rowCount()
        self.dataModel.removeRows(0, rowCount)

    def clear(self):
        self._removeAllFonts()
        self.setProperty("empty", "false")
        self.refreshStyleSheet()

    def setNoData(self):
        self._removeAllFonts()
        self.setProperty("empty", "true")
        self.refreshStyleSheet()

    def selectRowByIndex(self, index: QModelIndex):
        assert isinstance(index.model(), QSortFilterProxyModel)
        self.listView.setCurrentIndex(index)
        selectionModel = self.listView.selectionModel()
        selectionModel.select(index, QItemSelectionModel.Select)
        self.listView.scrollTo(index, QListView.PositionAtCenter)

    def empty(self):
        return self.dataModel.rowCount() == 0

    def selectFirstFont(self):
        index = self.filterModel.index(0, 0)
        self.selectRowByIndex(index)

    def selectFontByName(self, fontName: str):
        row = self.findFontRowByName(fontName)
        if row == -1:
            return False

        index = self.dataModel.index(row, 0)
        proxyIndex = self.filterModel.mapFromSource(index)
        self.selectRowByIndex(proxyIndex)
        return True

    def findFontRowByName(self, fontName: str):
        items = self.dataModel.findItems(fontName, Qt.MatchExactly)
        return items[0].row() if items else -1

    def _onSearchContentChanged(self, query: str):
        self.filterModel.setFilterFixedString(query)
        if self.filterModel.rowCount() > 0:
            proxyIndex = self.filterModel.index(0, 0)
            self.selectRowByIndex(proxyIndex)

    def hasFont(self, fontName: str):
        return self.findFontRowByName(fontName) != -1

    def canSelectFont(self):
        return self.filterModel.rowCount() > 0

    def selectedFont(self, index: Optional[QModelIndex] = None):
        if not index:
            index = self.listView.currentIndex()

        assert index.isValid(), "Index is invalid"
        return self.filterModel.mapToSource(index).data()

    def trySetFocusAndGoUp(self):
        self.listView.trySetFocusAndGoUp()

    def trySetFocusAndGoDown(self):
        self.listView.trySetFocusAndGoDown()
