from typing import Dict, List, Optional
from PyQt5.QtWidgets import QFileDialog, QListView
from PyQt5.QtCore import QModelIndex, QThreadPool, Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItem, QFont

from pyaxmlparser import APK
from loggat.app.components.dialogs import ErrorDialog, LoadingDialog
from loggat.app.util.signals import blockSignals
from .device_loader import DeviceLoader
from .package_loader import PackageLoader

from loggat.app.device import AdbClient, AdbDevice

from ...components.capture_pane import CapturePane
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane


class CapturePaneController:
    _pane: Optional[CapturePane]

    def __init__(self, adbHost: str, adbPort: int) -> None:
        self._client = AdbClient(adbHost, adbPort)
        self._lastSelectedDevice = None
        self._lastSelectedPackage = None
        self._nothingSelected = False
        self._pane = None

    def selectedDevice(self):
        return self._lastSelectedDevice

    def selectedPackage(self):
        return self._lastSelectedPackage

    def captureTargetSelected(self):
        return (
            self._nothingSelected == False
            and self._lastSelectedDevice is not None
            and self._lastSelectedPackage is not None
        )

    def takeControl(self, capturePane: CapturePane) -> None:
        self._pane = capturePane
        self._pane.reloadButton.clicked.connect(self._reloadButtonClicked)
        self._pane.deviceDropDown.currentTextChanged.connect(self._deviceChanged)
        self._pane.fromApkButton.clicked.connect(self._fromApkButtonClicked)
        self._pane.packagesList.doubleClicked.connect(self._packageSelected)
        self._pane.packagesList.activated.connect(self._packageSelected)
        self._pane.selectButton.clicked.connect(self._selectButtonClicked)
        self._pane.cancelButton.clicked.connect(self._pane.reject)
        self._pane.rejected.connect(self._rejected)
        self._nothingSelected = False

    def _rejected(self):
        self._nothingSelected = True

    def _packageSelected(self, index: QModelIndex):
        self._lastSelectedPackage = index.data()
        self._pane.accept()

    def _selectButtonClicked(self):
        index = self._pane.packagesList.currentIndex()
        self._packageSelected(index)

    def _reloadButtonClicked(self):
        deviceName = self._pane.deviceDropDown.currentText()
        self._deviceChanged(deviceName)

    def _deviceChanged(self, deviceName: str):
        self._pane.selectButton.setEnabled(False)
        self._pane.fromApkButton.setEnabled(False)
        self._lastSelectedDevice = deviceName
        self._pane.searchInput.setFocus()
        self._clearPackagesList()

        packageLoader = PackageLoader(self._client, deviceName)
        packageLoader.setStartDelay(750)
        packageLoader.signals.succeeded.connect(self._packageReloadSucceeded)
        packageLoader.signals.failed.connect(self._packageReloadFailed)
        QThreadPool.globalInstance().start(packageLoader)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Fetching packages...")
        self._loadingDialog.exec_()

    def _packageReloadSucceeded(self, packageList: List[str], selectedPackage: str):
        self._loadingDialog.close()
        self._setPackages(packageList)
        self._setSelectedPackage(selectedPackage)

    def _packageReloadFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        self.__setPackagesEmpty()

        messageBox = ErrorDialog()
        messageBox.setText(msgBrief)
        messageBox.setInformativeText(msgVerbose)
        messageBox.exec_()

    def _packageLoaderSucceeded(self, packageList: List[str], selectedPackage: str):
        self._packageReloadSucceeded(packageList, selectedPackage)
        self._pane.exec_()

    def _packageLoaderFailed(self, deviceName, deviceState):
        self._packageReloadFailed(deviceName, deviceState)
        self._pane.exec_()

    def _deviceLoaderSucceeded(self, deviceList: List[str], selectedDevice: str):
        self._setDevices(deviceList)
        self._setSelectedDevice(selectedDevice)
        self._lastSelectedDevice = selectedDevice
        self._loadingDialog.setText("Fetching packages...")

        packageLoader = PackageLoader(
            self._client, selectedDevice, self._lastSelectedPackage
        )
        packageLoader.setStartDelay(500)
        packageLoader.signals.succeeded.connect(self._packageLoaderSucceeded)
        packageLoader.signals.failed.connect(self._packageLoaderFailed)
        QThreadPool.globalInstance().start(packageLoader)

    def _deviceLoaderFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        messageBox = ErrorDialog()
        messageBox.setText(msgBrief)
        messageBox.setInformativeText(msgVerbose)
        messageBox.exec_()

    def startCaptureDialog(self):
        deviceLoader = DeviceLoader(self._client, self._lastSelectedDevice)
        deviceLoader.setStartDelay(500)
        deviceLoader.signals.succeeded.connect(self._deviceLoaderSucceeded)
        deviceLoader.signals.failed.connect(self._deviceLoaderFailed)
        QThreadPool.globalInstance().start(deviceLoader)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Connecting to ADB server...")
        self._loadingDialog.exec_()

    def _fromApkButtonClicked(self):
        openFileDialog = QFileDialog()
        openFileDialog.setFileMode(QFileDialog.ExistingFile)
        openFileDialog.setNameFilter("APK Files (*.apk)")

        if not openFileDialog.exec_():
            return

        selected_files = openFileDialog.selectedFiles()
        if not selected_files:
            return

        apk = APK(selected_files[0])
        packageName = apk.packagename

        if self._isPackageInstalled(packageName):
            self._lastSelectedPackage = packageName
            self._pane.accept()
        else:
            messageBox = ErrorDialog()
            messageBox.setText(f"Package '{packageName}' is not installed")
            text = "Please, install the package first (ADB -> Install APK)"
            messageBox.setInformativeText(text)
            messageBox.exec_()

    def _setDevices(self, devices: List[str]):
        with blockSignals(self._pane.deviceDropDown):
            self._pane.deviceDropDown.addItems(devices)
            self._clearPackagesList()

    def __setPackagesEmpty(self):
        self._pane.selectButton.setEnabled(False)
        self._pane.fromApkButton.setEnabled(False)
        self._clearPackagesList()

        item = QStandardItem()
        item.setSelectable(False)
        item.setEnabled(False)
        self._pane.dataModel.appendRow(item)

        item = QStandardItem("¯\_(ツ)_/¯")
        item.setSelectable(False)
        item.setEnabled(False)
        item.setData(Qt.AlignCenter, Qt.TextAlignmentRole)
        font = QFont("Arial")
        font.setPointSize(12)
        item.setFont(font)
        self._pane.dataModel.appendRow(item)

    def _setPackages(self, packages: List[str]):
        assert len(packages) > 0, "Non empty list expected"

        self._clearPackagesList()
        for package in packages:
            self._pane.dataModel.appendRow(QStandardItem(package))

        index = self._pane.filterModel.index(0, 0)
        self._selectPackagesListRowByIndex(index)

        self._pane.selectButton.setEnabled(True)
        self._pane.fromApkButton.setEnabled(True)

    def _clearPackagesList(self):
        rowCount = self._pane.dataModel.rowCount()
        self._pane.dataModel.removeRows(0, rowCount)

    def _setSelectedDevice(self, deviceName: str):
        with blockSignals(self._pane.deviceDropDown):
            self._pane.deviceDropDown.setCurrentText(deviceName)

    def _selectPackagesListRowByIndex(self, index: QModelIndex):
        selectionModel = self._pane.packagesList.selectionModel()
        selectionModel.clear()

        self._pane.packagesList.setCurrentIndex(index)
        selectionModel.select(index, QItemSelectionModel.Select)
        self._pane.packagesList.scrollTo(index, QListView.PositionAtCenter)

    def _findPackageItemByName(self, packageName: str):
        items = self._pane.dataModel.findItems(packageName, Qt.MatchExactly)
        return items[0] if items else None

    def _setSelectedPackage(self, packageName: str):
        item = self._findPackageItemByName(packageName)
        if not item:
            return

        proxyIndex = self._pane.filterModel.mapFromSource(item.index())
        self._selectPackagesListRowByIndex(proxyIndex)

    def _isPackageInstalled(self, packageName: str):
        return self._findPackageItemByName(packageName) is not None
