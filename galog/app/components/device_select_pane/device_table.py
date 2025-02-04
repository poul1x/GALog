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
    QStyle
)
from galog.app.components.capture_pane.body import SearchInputCanActivate
from galog.app.components.log_messages_pane.filter_model import FnFilterModel
from galog.app.util.qt_helper import selectRowByIndex
from .data_model import DataModel, FilterModel, Columns

from galog.app.util.table_view import TableView

from PyQt5.QtCore import QRect, QSize, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget, QStyledItemDelegate

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

    def addDevice(self, deviceSerial, deviceName, osName,  cpuArch):
        self.dataModel.addDevice(deviceSerial, deviceName, osName,  cpuArch)

    def addDeviceUnavailable(self, deviceSerial, errorMessage):
        self.dataModel.addUnavailableDevice(deviceSerial, errorMessage)
        row = self.dataModel.rowCount()
        columnSpan = self.dataModel.columnCount()
        self.tableView.setSpan(row - 1, 1, 1, columnSpan)

    def addTestDevices(self):
        self.addDevice(
            "RF8T213A4YW",
            "Google Pixel 4a (sunfish)",
            "Android 13",
            "arm-v64",
        )

        self.addDevice(
            "nm87weerty4",
            "Samsung SM-M127F (X00TD)",
            "Android 12",
            "arm-v64",
        )

        self.addDeviceUnavailable(
            "ert45tgf",
            "Error: failed to get XXXX asasa sas as as as a sa s a s as  as a sa s as a sa s as asa s",
        )

    def initUserInterface(self):
        self.dataModel = DataModel(self)
        self.filterModel = FilterModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)

        self.tableView = TableView(self)
        self.tableView.setModel(self.filterModel)
        self.tableView.setCornerButtonEnabled(False)
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
        hHeader.setSectionResizeMode(Columns.osName, QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.cpuArch, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.tableView.setColumnWidth(Columns.deviceSerial, 160)
        self.tableView.setColumnWidth(Columns.deviceName, 300)
        self.tableView.setColumnWidth(Columns.osName, 100)

        ############################################################
        # Layout
        ############################################################

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.searchInput = SearchInputCanActivate(self)
        self.searchInput.textChanged.connect(self.onSearchContentChanged)
        hBoxLayout.addWidget(self.searchInput, 1)
        self.searchInput.setPlaceholderText("Search device by name or serial")

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addWidget(self.tableView)
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)
        self.setLayout(vBoxLayout)

        self.addTestDevices()
        self.addTestDevices()
        # self.addTestDevices()
        # self.addTestDevices()

    def onSearchContentChanged(self, query: str):
        self.filterModel.setFilterFixedString(query)
        if self.filterModel.rowCount() > 0:
            proxyIndex = self.filterModel.index(0, 0)
            selectRowByIndex(self.tableView, proxyIndex)
