from typing import Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QStandardItem
from PyQt5.QtCore import QRect, QSize, Qt, QSortFilterProxyModel, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QApplication,
    QComboBox,
)
from galog.app.components.capture_pane.body import SearchInputCanActivate
from galog.app.util.qt_helper import selectRowByIndex
from .data_model import DataModel, Columns

from galog.app.util.table_view import TableView

from PyQt5.QtCore import QRect, QSize, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget

from enum import Enum,auto

class SearchType(int, Enum):
    Serial = 0
    Name = auto()


class DeviceTable(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def addDevice(self, deviceSerial, deviceName, buildInfo, cpuAbi):
        self.dataModel.addDevice(
            QStandardItem(deviceSerial),
            QStandardItem(deviceName),
            QStandardItem(buildInfo),
            QStandardItem(cpuAbi),
        )

    def addDeviceUnavailable(self, deviceSerial, errorMessage):
        row = self.dataModel.rowCount()
        columnSpan = self.dataModel.columnCount()
        self.tableView.setSpan(row, 1, 1, columnSpan)

        self.dataModel.addDevice(
            QStandardItem(deviceSerial),
            QStandardItem(errorMessage),
            QStandardItem(""),
            QStandardItem(""),
        )

    def addTestDevices(self):
        self.addDevice(
            "RF8T213A4YW",
            "Google Pixel 4a (sunfish)",
            "Android 12 (API Level: 23-31)",
            "arm-v64",
        )

        self.addDevice(
            "nm87weerty4",
            "Samsung SM-M127F (m12nsxx)",
            "Android 12 (API Level: ?-?)",
            "arm-v64",
        )

        self.addDeviceUnavailable(
            "ert45tgf",
            "Error: failed to get XXXX",
        )

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)

        self.tableView = TableView()
        self.tableView.setModel(self.filterModel)
        self.tableView.setCornerButtonEnabled(False)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.setTabKeyNavigation(False)
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
        hHeader.setSectionResizeMode(Columns.buildInfo, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.cpuAbi, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tableView.setColumnWidth(Columns.deviceSerial, 160)
        self.tableView.setColumnWidth(Columns.deviceName, 300)
        self.tableView.setColumnWidth(Columns.buildInfo, 300)

        ############################################################
        # Layout
        ############################################################

        hBoxLayout = QHBoxLayout()
        self.searchInput = SearchInputCanActivate(self)
        self.searchInput.textChanged.connect(self.onSearchContentChanged)
        hBoxLayout.addWidget(self.searchInput, 1)

        self.searchTypeDropdown = QComboBox(self)
        self.searchTypeDropdown.addItem("Name")
        self.searchTypeDropdown.addItem("Serial")
        self.searchTypeDropdown.currentIndexChanged.connect(self.onSearchTypeChanged)
        self.searchTypeDropdown.currentIndexChanged.emit(SearchType.Name)
        hBoxLayout.addWidget(self.searchTypeDropdown)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addWidget(self.tableView)
        vBoxLayout.addLayout(hBoxLayout)
        self.setLayout(vBoxLayout)

        # self.addTestDevices()
        # self.addTestDevices()
        # self.addTestDevices()
        # self.addTestDevices()

    def onSearchTypeChanged(self, index: int):
        self.filterModel.setFilterKeyColumn(index)
        if index == SearchType.Name:
            self.searchInput.setPlaceholderText("Search device by name")
        else:
            self.searchInput.setPlaceholderText("Search device by serial")

    def onSearchContentChanged(self, query: str):
        self.filterModel.setFilterFixedString(query)
        if self.filterModel.rowCount() > 0:
            proxyIndex = self.filterModel.index(0, 0)
            selectRowByIndex(self.tableView, proxyIndex)

