from enum import Enum, auto
from typing import Optional

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QObject


class Columns(int, Enum):
    deviceSerial = 0
    deviceName = auto()
    cpuArch = auto()
    osName = auto()
    apiLevels = auto()

class DataModel(QStandardItemModel):
    def __init__(self, parent):
        super().__init__(0, len(Columns), parent)
        self.setHorizontalHeaderLabels(
            [
                "Device Serial",
                "Device Name",
                "CPU Arch",
                "OS Info",
                "API Levels",
            ]
        )

    def addValidDevice(
        self,
        deviceSerial: str,
        deviceName: str,
        osInfo: str,
        cpuArch: str,
        apiLevels: str,
    ):
        itemSerial = QStandardItem(deviceSerial)
        itemSerial.setData(True, Qt.UserRole)

        self.appendRow(
            [
                itemSerial,
                QStandardItem(deviceName),
                QStandardItem(cpuArch),
                QStandardItem(osInfo),
                QStandardItem(apiLevels),
            ]
        )

    def addInvalidDevice(
        self,
        deviceSerial: str,
        errorMessage: str,
    ):
        itemSerial = QStandardItem(deviceSerial)
        itemSerial.setData(False, Qt.UserRole)

        self.appendRow(
            [
                itemSerial,
                QStandardItem(errorMessage),
            ]
        )

        item = self.item(self.rowCount() - 1, Columns.deviceSerial)
        item.setData(False, Qt.UserRole)

    def removeAllDevices(self):
        self.removeRows(0, self.rowCount())

    def setEmptyDeviceList(self):
        self.removeAllDevices()

        item = QStandardItem("¯\_(ツ)_/¯")
        item.setSelectable(False)
        item.setEnabled(False)
        item.setData(Qt.AlignCenter, Qt.TextAlignmentRole)
        self.appendRow(item)

    def findDeviceRowBySerial(self, serial: str):
        items = self.findItems(serial, Qt.MatchExactly, Columns.deviceSerial)
        return items[0].row() if items else -1


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        regex = self.filterRegExp()
        sourceModel = self.sourceModel()
        assert isinstance(sourceModel, DataModel)
        serial = sourceModel.index(sourceRow, Columns.deviceSerial, sourceParent).data()
        name = sourceModel.index(sourceRow, Columns.deviceName, sourceParent).data()
        return regex.indexIn(serial) != -1 or regex.indexIn(name) != -1