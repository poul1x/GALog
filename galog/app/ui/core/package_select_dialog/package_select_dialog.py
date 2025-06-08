from typing import List
from zipfile import BadZipFile

from PyQt5.QtCore import QModelIndex, Qt, QThreadPool
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QVBoxLayout, QWidget

from galog.app.apk_info import APK
from galog.app.app_state import AppState, LastSelectedPackage
from galog.app.ui.actions.list_packages import ListPackagesAction
from galog.app.ui.base.dialog import Dialog
from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.ui.actions.install_app.action import InstallAppAction
from galog.app.device import AdbClient
from galog.app.device.errors import DeviceError, DeviceNotFound
from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.msgbox import msgBoxErr, msgBoxPrompt

from ..device_select_dialog import DeviceSelectDialog
from .button_bar import ButtonBar
from .load_options import PackagesLoadOptions
from .packages_list import PackagesList


class PackageSelectDialog(Dialog):
    def __init__(self, appState: AppState, parent: QWidget):
        super().__init__(parent)
        self._appState = appState
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowTitle("Select Package")
        self.setRelativeGeometry(0.8, 0.6, 800, 600)
        self.setFixedMaxSize(800, 600)
        self.setFixedMinSize(600, 400)
        self.moveToCenter()
        self.initUserInterface()
        self.initUserInputHandlers()
        self.initFocusPolicy()
        self._refreshSelectedDevice()

    def _refreshSelectedDevice(self):
        assert self._appState.lastSelectedDevice is not None
        deviceName = self._appState.lastSelectedDevice.displayName
        self.packagesLoadOptions.setDeviceName(deviceName)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.packagesList.searchInput.setFocus()
        elif helper.isCtrlRPressed():
            self.packagesLoadOptions.reloadButton.clicked.emit()
        else:
            super().keyPressEvent(event)

    def initUserInputHandlers(self):
        self.packagesLoadOptions.reloadButton.clicked.connect(self._reloadButtonClicked)
        self.packagesList.listView.rowActivated.connect(self._packageSelected)

        self.buttonBar.fromApkButton.clicked.connect(self._fromApkButtonClicked)
        self.buttonBar.selectButton.clicked.connect(self._selectButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

        searchInput = self.packagesList.searchInput
        searchInput.returnPressed.connect(self._packageMayBeSelected)
        searchInput.textChanged.connect(self._manageSelectButtonOnOff)
        searchInput.arrowUpPressed.connect(self._tryFocusPackagesListAndGoUp)
        searchInput.arrowDownPressed.connect(self._tryFocusPackagesListAndGoDown)

        self.packagesLoadOptions.deviceSelectButton.clicked.connect(
            self._selectAnotherDevice
        )

    def _manageSelectButtonOnOff(self):
        canSelect = self.packagesList.canSelectPackage()
        self.buttonBar.selectButton.setEnabled(canSelect)

    def initUserInterface(self):
        self.setWindowTitle("New capture")
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.packagesLoadOptions = PackagesLoadOptions(self)
        self.packagesList = PackagesList(self)
        self.buttonBar = ButtonBar(self)

        layout.addWidget(self.packagesLoadOptions)
        layout.addWidget(self.packagesList)
        layout.addWidget(self.buttonBar)
        self.setLayout(layout)

    def initFocusPolicy(self):
        self.packagesLoadOptions.deviceSelectButton.setFocusPolicy(Qt.NoFocus)
        self.packagesLoadOptions.actionDropDown.setFocusPolicy(Qt.NoFocus)
        self.packagesLoadOptions.reloadButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.selectButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.fromApkButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.NoFocus)

        self.packagesList.searchInput.setFocus()
        self.setTabOrder(self.packagesList.searchInput, self.packagesList.listView)
        self.setTabOrder(self.packagesList.listView, self.packagesList.searchInput)

    def _tryFocusPackagesListAndGoUp(self):
        self.packagesList.trySetFocusAndGoUp()

    def _tryFocusPackagesListAndGoDown(self):
        self.packagesList.trySetFocusAndGoDown()

    def _selectDefaultPackage(self, packages: List[str]):
        #
        # Select package which was previously set
        # If package is not present or no packages was previously set
        # Select the first one by default
        #

        if self._appState.lastSelectedPackage is not None:
            packageName = self._appState.lastSelectedPackage.name
            if self.packagesList.selectPackageByName(packageName):
                return

        assert len(packages) > 0
        self.packagesList.selectPackageByName(packages[0])

    def _setPackages(self, packages: List[str]):
        self.packagesList.clear()
        for package in packages:
            self.packagesList.addPackage(package)

    def adbClient(self):
        return AdbClient(
            self._appState.adb.ipAddr,
            int(self._appState.adb.port),
        )

    def exec_(self):
        self._refreshPackagesList()
        return super().exec_()

    def _refreshPackagesList(self):
        deviceSerial = self._appState.lastSelectedDevice.serial
        action = ListPackagesAction(self.adbClient(), self)
        action.setAllowSelectAnotherDevice(True)

        packages = action.listPackages(deviceSerial)
        if packages is not None:
            self.buttonBar.fromApkButton.setEnabled(True)
            self._setPackages(packages)
            if self.packagesList.canSelectPackage():
                self.buttonBar.selectButton.setEnabled(True)
                self._selectDefaultPackage(packages)
        else:
            self.buttonBar.selectButton.setEnabled(False)
            self.buttonBar.fromApkButton.setEnabled(False)
            self.packagesList.setNoData()
            if action.needSelectAnotherDevice():
                self._selectAnotherDevice(autoSelect=True)

    def _reloadButtonClicked(self):
        self._refreshPackagesList()

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
            msgBoxErr(msgBrief, msgVerbose, self)
            return

        if self.packagesList.has(packageName):
            self.packagesList.selectPackageByName(packageName)
            self._selectButtonClicked()
            return

        msgBrief = "Package not installed"
        prompt = f"This app is not present on the device. Do you want to install and run it?"
        if not msgBoxPrompt(msgBrief, prompt, self):
            return

        deviceSerial = self._appState.lastSelectedDevice.serial
        action = InstallAppAction(self.adbClient(), self)
        if not action.installApp(deviceSerial, selectedFiles[0]):
            return

        self.packagesList.addPackage(packageName)
        self.packagesList.selectPackageByName(packageName)
        self._selectButtonClicked()

    def _packageSelected(self, index: QModelIndex):
        packageName = self.packagesList.selectedPackage(index)
        selectedAction = self.packagesLoadOptions.runAppAction()
        selectedPackage = LastSelectedPackage(packageName, selectedAction)
        self._appState.lastSelectedPackage = selectedPackage
        self.accept()

    def _packageMayBeSelected(self):
        index = self.packagesList.listView.currentIndex()
        if not index.isValid():
            return

        self._packageSelected(index)

    def _selectButtonClicked(self):
        self._packageSelected(self.packagesList.listView.currentIndex())

    def _selectAnotherDevice(self, autoSelect: bool = False):
        deviceSelectDialog = DeviceSelectDialog(self._appState, self.parent())
        deviceSelectDialog.setDeviceAutoSelect(autoSelect)
        result = deviceSelectDialog.exec_()
        if result == 0:
            return

        self.packagesList.searchInput.setFocus()
        self._refreshSelectedDevice()
        self._refreshPackagesList()
