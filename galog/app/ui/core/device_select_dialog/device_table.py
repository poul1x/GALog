from enum import Enum, auto
from typing import Optional

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from galog.app.ui.base.table_view import TableView
from galog.app.ui.base.widget import Widget
from galog.app.ui.reusable.search_input import SearchInput

from .data_model import Columns, DataModel, FilterModel


class SearchType(int, Enum):
    Serial = 0
    Name = auto()


class DeviceTable(Widget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.clear()

    def addValidDevice(
        self,
        deviceSerial: str,
        deviceName: str,
        osInfo: str,
        cpuArch: str,
        apiLevels: str,
    ):
        self.dataModel.addValidDevice(
            deviceSerial,
            deviceName,
            osInfo,
            cpuArch,
            apiLevels,
        )

    def addInvalidDevice(
        self,
        deviceSerial: str,
        errorMessage: str,
    ):
        self.dataModel.addInvalidDevice(deviceSerial, errorMessage)

    def sort(self):
        self.tableView.sortByColumn(Columns.displayName, Qt.AscendingOrder)

    def clear(self):
        self.dataModel.removeAllDevices()
        self.setProperty("empty", "false")
        self.refreshStyleSheet()

    def setNoData(self):
        self.dataModel.removeAllDevices()
        self.setProperty("empty", "true")
        self.refreshStyleSheet()

    def selectRowByIndex(self, index: QModelIndex):
        assert isinstance(index.model(), FilterModel)
        self.tableView.setCurrentIndex(index)
        selectionModel = self.tableView.selectionModel()
        selectionModel.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)  # fmt: skip
        self.tableView.scrollTo(index, QTableView.PositionAtCenter)

    def selectTheOnlyOneDevice(self):
        if self.filterModel.rowCount() == 1:
            index = self.filterModel.index(0, Columns.serial)
            if index.data(Qt.UserRole):  # isValid
                self.selectRowByIndex(index)
                return True

        return False

    def selectDeviceBySerial(self, serial: str):
        row = self.dataModel.findDeviceRowBySerial(serial)
        if row == -1:
            return False

        index = self.dataModel.index(row, Columns.serial)
        proxyIndex = self.filterModel.mapFromSource(index)
        self.selectRowByIndex(proxyIndex)
        return True

    def selectedDevice(self, index: Optional[QModelIndex] = None):
        if not index:
            index = self.tableView.currentIndex()

        assert index.isValid(), "Index is invalid"
        realIndex = self.filterModel.mapToSource(index)

        serialIndex = self.dataModel.index(realIndex.row(), Columns.serial)
        nameIndex = self.dataModel.index(realIndex.row(), Columns.displayName)
        return serialIndex.data(), nameIndex.data(), serialIndex.data(Qt.UserRole)

    def canSelectDevice(self):
        return self.filterModel.rowCount() > 0

    def _applySpans(self):
        rowCount = self.filterModel.rowCount()
        columnCount = self.filterModel.columnCount()

        for i in range(rowCount):
            index = self.filterModel.index(i, Columns.serial)
            if index.data(Qt.UserRole) == True:
                if self.tableView.columnSpan(i, 1) > 1:  # Restore span to 1
                    self.tableView.setSpan(i, 1, 1, 1)
            else:
                self.tableView.setSpan(i, 1, 1, columnCount - 1)  # Set span to > 1

    def initUserInterface(self):
        self.dataModel = DataModel(self)
        self.filterModel = FilterModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)

        # Fix spans on sorting by columns
        self.filterModel.layoutChanged.connect(self._applySpans)
        self.dataModel.rowsInserted.connect(self._applySpans)

        self.tableView = TableView(self)
        self.tableView.setModel(self.filterModel)
        self.tableView.setCornerButtonEnabled(False)
        self.tableView.setSortingEnabled(True)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.setTabKeyNavigation(False)
        self.tableView.setWordWrap(False)
        self.tableView.setShowGrid(False)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        vHeader = self.tableView.verticalHeader()
        vHeader.setVisible(False)

        hHeader = self.tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.serial, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.displayName, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.cpuArch, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.osName, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.apiLevels, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tableView.setColumnWidth(Columns.serial, 160)
        self.tableView.setColumnWidth(Columns.displayName, 300)

        ############################################################
        # Layout
        ############################################################

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.searchInput = SearchInput(self)
        self.searchInput.setPlaceholderText("Search device by name or serial")
        self.searchInput.textChanged.connect(self._searchContentChanged)
        self.searchInput.textChanged.connect(self._applySpans)
        hBoxLayout.addWidget(self.searchInput, 1)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addWidget(self.tableView)
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)
        self.setLayout(vBoxLayout)

    def _refreshBackground(self):
        filterModel = self.filterModel
        hasResults = "true" if filterModel.hasResults() else "false"
        self.setProperty("hasResults", hasResults)
        self.refreshStyleSheet()

    def _searchContentChanged(self, query: str):
        self.filterModel.setFilterFixedString(query)
        if self.filterModel.hasResults():
            proxyIndex = self.filterModel.index(0, 0)
            self.selectRowByIndex(proxyIndex)

        self._refreshBackground()

    def trySetFocusAndGoUp(self):
        self.tableView.trySetFocusAndGoUp()

    def trySetFocusAndGoDown(self):
        self.tableView.trySetFocusAndGoDown()
