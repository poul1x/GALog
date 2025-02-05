from typing import Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QStandardItem
from PyQt5.QtCore import (
    QRect,
    QSize,
    Qt,
    QSortFilterProxyModel,
    QModelIndex,
    QItemSelectionModel,
)
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QApplication,
    QStyle,
)
from galog.app.components.capture_pane.body import SearchInputCanActivate
from galog.app.components.log_messages_pane.filter_model import FnFilterModel
from galog.app.util.qt_helper import selectRowByIndex
from .data_model import DataModel, FilterModel, Columns

from galog.app.util.table_view import TableView

from PyQt5.QtCore import QRect, QSize, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QWidget,
    QStyledItemDelegate,
)

from enum import Enum, auto


class SearchType(int, Enum):
    Serial = 0
    Name = auto()


class DeviceTable(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("DeviceTable")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def currentIndex(self):
        return self.tableView.currentIndex()

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
        self.tableView.sortByColumn(Columns.deviceName, Qt.AscendingOrder)

    def clear(self):
        self.dataModel.removeAllDevices()

    def setNoData(self):
        self.dataModel.setEmptyDeviceList()

    def selectDeviceBySerial(self, serial: str):
        row = self.dataModel.findDeviceRowBySerial(serial)
        if row == -1:
            return False


        selectionModel = self.tableView.selectionModel()
        index = self.dataModel.index(row, Columns.deviceSerial)

        proxyIndex = self.filterModel.mapFromSource(index)
        self.tableView.setCurrentIndex(proxyIndex)

        selectionModel.select(proxyIndex, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.tableView.scrollTo(proxyIndex, QTableView.PositionAtCenter)

        return True

    def selectedDeviceSerial(self, index: Optional[QModelIndex] = None):
        if not index:
            index = self.tableView.currentIndex()

        assert index.isValid(), "Index is invalid"
        realIndex = self.filterModel.mapToSource(index)

        serialIndex = self.dataModel.index(realIndex.row(), Columns.deviceSerial)
        return serialIndex.data(), serialIndex.data(Qt.UserRole)

    def _applySpans(self):
        rowCount = self.filterModel.rowCount()
        columnCount = self.filterModel.columnCount()

        for i in range(rowCount):
            index = self.filterModel.index(i, Columns.deviceSerial)
            if index.data(Qt.UserRole) == True:
                if self.tableView.columnSpan(i, 1) > 1: # Restore span to 1
                    self.tableView.setSpan(i, 1, 1, 1)
            else:
                self.tableView.setSpan(i, 1, 1, columnCount - 1) # Set span to > 1


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

        font = QFont("Arial")
        font.setPixelSize(19)
        self.tableView.setFont(font)

        hHeader = self.tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.deviceSerial, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.deviceName, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.cpuArch, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.osName, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.apiLevels, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tableView.setColumnWidth(Columns.deviceSerial, 160)
        self.tableView.setColumnWidth(Columns.deviceName, 300)

        ############################################################
        # Layout
        ############################################################

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.searchInput = SearchInputCanActivate(self)
        self.searchInput.textChanged.connect(self.onSearchContentChanged)
        hBoxLayout.addWidget(self.searchInput, 1)
        self.searchInput.setPlaceholderText("Search device by name or serial")
        self.searchInput.textChanged.connect(self._applySpans)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addWidget(self.tableView)
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)
        self.setLayout(vBoxLayout)


    def onSearchContentChanged(self, query: str):
        self.filterModel.setFilterFixedString(query)
        if self.filterModel.rowCount() > 0:
            proxyIndex = self.filterModel.index(0, 0)
            selectRowByIndex(self.tableView, proxyIndex)
