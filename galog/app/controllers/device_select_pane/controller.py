from typing import List, Optional
from zipfile import BadZipFile

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, Qt, QThreadPool
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QFileDialog, QListView

from galog.app.apk_info import APK
from galog.app.components.capture_pane import RunAppAction
from galog.app.components.dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.util.message_box import showErrorMsgBox
from galog.app.util.signals import blockSignals

from ...components.device_select_pane import DeviceSelectPane
from .device_loader import DeviceLoader
from .package_loader import PackageLoader


class DeviceSelectPaneController:
    _pane: Optional[DeviceSelectPane]

    def __init__(self) -> None:
        self._client = AdbClient()
        self._lastSelectedDevice = None
        self._nothingSelected = False
        self._pane = None

    def selectedDevice(self):
        assert self.isDeviceSelected()
        return self._lastSelectedDevice

    def isDeviceSelected(self):
        return self._lastSelectedDevice is not None

    def takeControl(self, deviceSelectPane: DeviceSelectPane) -> None:
        self._pane = deviceSelectPane
        self._setAppRunAction(self._lastSelectedAction)
        self._pane.reloadButton.clicked.connect(self._reloadButtonClicked)
        self._pane.deviceDropDown.currentTextChanged.connect(self._deviceChanged)
        self._pane.fromApkButton.clicked.connect(self._fromApkButtonClicked)
        self._pane.packagesList.doubleClicked.connect(self._packageSelected)
        self._pane.packagesList.rowActivated.connect(self._packageSelected)
        self._pane.searchInput.activate.connect(self._packageMayBeSelected)
        self._pane.searchInput.textChanged.connect(self._searchQueryChanged)
        self._pane.selectButton.clicked.connect(self._selectButtonClicked)
        self._pane.cancelButton.clicked.connect(self._pane.reject)
        self._pane.rejected.connect(self._rejected)
        self._nothingSelected = False

    def startCaptureDialog(self):
        deviceLoader = DeviceLoader(self._client, self._lastSelectedDevice)
        deviceLoader.setStartDelay(500)
        deviceLoader.signals.succeeded.connect(self._deviceLoaderSucceeded)
        deviceLoader.signals.failed.connect(self._deviceLoaderFailed)
        QThreadPool.globalInstance().start(deviceLoader)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Connecting to ADB server...")
        self._loadingDialog.exec_()

    def _searchQueryChanged(self, query: str):
        self._pane.filterModel.setFilterFixedString(query)
        if self._pane.filterModel.rowCount() > 0:
            proxyIndex = self._pane.filterModel.index(0, 0)
            self._selectPackagesListRowByIndex(proxyIndex)

    def _setAppRunAction(self, action: RunAppAction):
        i = self._pane.actionDropDown.findData(action, Qt.UserRole)
        assert i != -1, "Current action must be present in RunAppAction"
        self._pane.actionDropDown.setCurrentIndex(i)

    def _rejected(self):
        self._nothingSelected = True


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
        self._setPackagesEmpty()
        self._lastSelectedPackage = None
        showErrorMsgBox(msgBrief, msgVerbose)

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
        self._lastSelectedDevice = None
        self._lastSelectedPackage = None
        showErrorMsgBox(msgBrief, msgVerbose)

    def _fromApkButtonClicked(self):
        openFileDialog = QFileDialog()
        openFileDialog.setFileMode(QFileDialog.ExistingFile)
        openFileDialog.setNameFilter("APK Files (*.apk)")

        if not openFileDialog.exec_():
            return

        selectedFiles = openFileDialog.selectedFiles()
        if not selectedFiles:
            return

        try:
            apk = APK(selectedFiles[0])
            packageName = apk.packagename
            if not packageName:
                raise ValueError("Not a valid APK")

        except (BadZipFile, ValueError):
            msgBrief = "Operation failed"
            msgVerbose = "Provided file is not a valid APK"
            showErrorMsgBox(msgBrief, msgVerbose)
            return

        if not self._isPackageInstalled(packageName):
            msgBrief = "Package not installed"
            msgVerbose = f"Please, install the package '{packageName}' first"
            showErrorMsgBox(msgBrief, msgVerbose)
            return

        self._lastSelectedPackage = packageName
        self._pane.accept()

    def _setDevices(self, devices: List[str]):

        self._clearPackagesList()
        for package in packages:
            self._pane.dataModel.appendRow(QStandardItem(package))

        index = self._pane.filterModel.index(0, 0)
        self._selectPackagesListRowByIndex(index)





        self._pane.selectButton.setEnabled(True)
        self._pane.fromApkButton.setEnabled(True)
        with blockSignals(self._pane.deviceDropDown):
            self._pane.deviceDropDown.addItems(devices)
            self._clearPackagesList()

    def _setPackagesEmpty(self):
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

    def _clearDevices(self):
        rowCount = self._pane.dataModel.rowCount()
        self._pane.dataModel.removeRows(0, rowCount)

    def _selectPackagesListRowByIndex(self, index: QModelIndex):
        selectionModel = self._pane.tableView.selectionModel()
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
