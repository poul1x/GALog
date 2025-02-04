from enum import Enum, auto
from typing import Optional

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QObject

# ro.product.cpu.abi arm/arm64
# ro.product.model # ro.product.manufacturer (ro.product.name)
# ro.product.device
# Android ver adb shell getprop ro.build.version.release
# API level adb shell getprop ro.build.version.sdk
# API min level ro.build.version.min_supported_target_sdk
# Google Pixel 4a (sunfish)
# Android 12 (API Level: 23-31)
# arm-v64


class Columns(int, Enum):
    deviceSerial = 0
    deviceName = auto()
    osName = auto()
    cpuArch = auto()


class DataModel(QStandardItemModel):
    def __init__(self, parent):
        super().__init__(0, len(Columns), parent)
        labels = ["Device Serial", "Device Name", "OS Name", "CPU Arch"]
        self.setHorizontalHeaderLabels(labels)

    def addDevice(
        self,
        deviceSerial: str,
        deviceName: str,
        osName: str,
        cpuArch: str,
    ):
        self.appendRow(
            [
                QStandardItem(deviceSerial),
                QStandardItem(deviceName),
                QStandardItem(osName),
                QStandardItem(cpuArch),
            ]
        )

    def addUnavailableDevice(
        self,
        deviceSerial: str,
        errorMessage: str,
    ):
        self.appendRow(
            [
                QStandardItem(deviceSerial),
                QStandardItem(errorMessage),
            ]
        )


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
