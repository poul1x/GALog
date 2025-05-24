from typing import Optional

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView, QVBoxLayout, QWidget

from galog.app.ui.reusable import SearchInput
from galog.app.ui.base.list_view import BaseListView


class PackagesList(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("PackagesList")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.listView = BaseListView(self)
        self.listView.setEditTriggers(QListView.NoEditTriggers)

        self.dataModel = QStandardItemModel(self)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)
        self.listView.setModel(self.filterModel)
        layout.addWidget(self.listView)

        self.searchInput = SearchInput(self)
        self.searchInput.setPlaceholderText("Search package")
        self.searchInput.textChanged.connect(self._onSearchContentChanged)
        layout.addWidget(self.searchInput)

        self.setLayout(layout)

    def addPackage(self, packageName: str):
        self.dataModel.appendRow(QStandardItem(packageName))

    def clear(self):
        rowCount = self.dataModel.rowCount()
        self.dataModel.removeRows(0, rowCount)

    def setNoData(self):
        self.clear()

        item = QStandardItem()
        item.setSelectable(False)
        item.setEnabled(False)
        self.dataModel.appendRow(item)

        item = QStandardItem("¯\_(ツ)_/¯")
        item.setSelectable(False)
        item.setEnabled(False)
        item.setData(Qt.AlignCenter, Qt.TextAlignmentRole)
        self.dataModel.appendRow(item)

    def selectRowByIndex(self, index: QModelIndex):
        assert isinstance(index.model(), QSortFilterProxyModel)
        self.listView.setCurrentIndex(index)
        selectionModel = self.listView.selectionModel()
        selectionModel.select(index, QItemSelectionModel.Select)
        self.listView.scrollTo(index, QListView.PositionAtCenter)

    def selectPackageByName(self, packageName: str):
        row = self.findPackageRowByName(packageName)
        if row == -1:
            return False

        index = self.dataModel.index(row, 0)
        proxyIndex = self.filterModel.mapFromSource(index)
        self.selectRowByIndex(proxyIndex)
        return True

    def findPackageRowByName(self, packageName: str):
        items = self.dataModel.findItems(packageName, Qt.MatchExactly)
        return items[0].row() if items else -1

    def _onSearchContentChanged(self, query: str):
        self.filterModel.setFilterFixedString(query)
        if self.filterModel.rowCount() > 0:
            proxyIndex = self.filterModel.index(0, 0)
            self.selectRowByIndex(proxyIndex)

    def has(self, packageName: str):
        return self.findPackageRowByName(packageName) != -1

    def canSelectPackage(self):
        return self.filterModel.rowCount() > 0

    def selectedPackage(self, index: Optional[QModelIndex] = None):
        if not index:
            index = self.listView.currentIndex()

        assert index.isValid(), "Index is invalid"
        return self.filterModel.mapToSource(index).data()

    def trySetFocusAndGoUp(self):
        self.listView.trySetFocusAndGoUp()

    def trySetFocusAndGoDown(self):
        self.listView.trySetFocusAndGoDown()