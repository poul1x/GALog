from typing import List
from zipfile import BadZipFile

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from galog.app.apk_info import APK
from galog.app.device import adbClient
from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from galog.app.settings.models import LastSelectedPackage
from galog.app.settings.settings import readSessionSettings, readSettings
from galog.app.ui.actions.install_app.action import InstallAppAction
from galog.app.ui.actions.list_packages import ListPackagesAction
from galog.app.ui.base.dialog import Dialog
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from ..device_select_dialog import DeviceSelectDialog
from .button_bar import BottomButtonBar
from .load_options import PackagesLoadOptions
from .packages_list import PackagesList


class PackageSelectDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._settings = readSettings()
        self._sessionSettings = readSessionSettings()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowTitle("Select Package")
        self.setRelativeGeometry(0.8, 0.6, 800, 600)
        self.setFixedMaxSize(800, 600)
        self.setFixedMinSize(600, 400)
        self.moveToCenter()
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initFocusPolicy()
        self._refreshSelectedDevice()

    def _refreshSelectedDevice(self):
        assert self._sessionSettings.lastSelectedDevice is not None
        deviceName = self._sessionSettings.lastSelectedDevice.displayName
        self.packagesLoadOptions.setDeviceName(deviceName)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.packagesList.searchInput.setFocus()
        elif helper.isCtrlRPressed():
            self.packagesLoadOptions.reloadButton.clicked.emit()
        else:
            super().keyPressEvent(event)

    def _initUserInputHandlers(self):
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

    def _initUserInterface(self):
        self.setWindowTitle("New capture")
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.packagesLoadOptions = PackagesLoadOptions(self)
        self.packagesList = PackagesList(self)
        self.buttonBar = BottomButtonBar(self)

        layout.addWidget(self.packagesLoadOptions)
        layout.addWidget(self.packagesList)
        layout.addWidget(self.buttonBar)
        self.setLayout(layout)

    def _initFocusPolicy(self):
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

        if self._sessionSettings.lastSelectedPackage is not None:
            packageName = self._sessionSettings.lastSelectedPackage.name
            if self.packagesList.selectPackageByName(packageName):
                return

        assert len(packages) > 0
        self.packagesList.selectPackageByName(packages[0])

    def _setPackages(self, packages: List[str]):
        self.packagesList.clear()
        for package in packages:
            self.packagesList.addPackage(package)

    def exec_(self):
        self._refreshPackagesList()
        return super().exec_()

    def _refreshPackagesList(self):
        deviceSerial = self._sessionSettings.lastSelectedDevice.serial
        action = ListPackagesAction(adbClient(), self)
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

        if openFileDialog.exec_() == QFileDialog.Rejected:
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
        prompt = f"This app is not present on the device. Do you want to install and run it?"  # fmt: skip
        if not msgBoxPrompt(msgBrief, prompt, self):
            return

        deviceSerial = self._sessionSettings.lastSelectedDevice.serial
        action = InstallAppAction(adbClient(), self)
        if not action.installApp(deviceSerial, selectedFiles[0]):
            return

        self.packagesList.addPackage(packageName)
        self.packagesList.selectPackageByName(packageName)
        self._selectButtonClicked()

    def _packageSelected(self, index: QModelIndex):
        packageName = self.packagesList.selectedPackage(index)
        selectedAction = self.packagesLoadOptions.runAppAction()
        selectedPackage = LastSelectedPackage.new(packageName, selectedAction)
        self._sessionSettings.lastSelectedPackage = selectedPackage
        self.accept()

    def _packageMayBeSelected(self):
        index = self.packagesList.listView.currentIndex()
        if not index.isValid():
            return

        self._packageSelected(index)

    def _selectButtonClicked(self):
        self._packageSelected(self.packagesList.listView.currentIndex())

    def _selectAnotherDevice(self, autoSelect: bool = False):
        deviceSelectDialog = DeviceSelectDialog(self.parent())
        deviceSelectDialog.setDeviceAutoSelect(autoSelect)

        if deviceSelectDialog.exec_() == DeviceSelectDialog.Rejected:
            return

        self.packagesList.searchInput.setFocus()
        self._refreshSelectedDevice()
        self._refreshPackagesList()
