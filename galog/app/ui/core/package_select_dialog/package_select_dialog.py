from typing import List
from zipfile import BadZipFile

from PyQt5.QtCore import QModelIndex, Qt, QThreadPool
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QVBoxLayout, QWidget

from galog.app.apk_info import APK
from galog.app.app_state import AppState, LastSelectedPackage
from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.ui.actions.install_app.controller import InstallAppController
from galog.app.device import AdbClient
from galog.app.device.errors import DeviceError, DeviceNotFound
from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.msgbox import msgBoxErr, msgBoxPrompt

from ..device_select_dialog import DeviceSelectDialog
from .button_bar import ButtonBar
from .load_options import PackagesLoadOptions
from .package_loader import PackageLoader
from .packages_list import PackagesList


class PackageSelectDialog(QDialog):
    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowCloseButtonHint

    def __init__(self, appState: AppState, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self._appState = appState
        self.setObjectName("PackageSelectDialog")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()
        self.initUserInputHandlers()
        self.initFocusPolicy()
        self.setGeometryAuto()
        self.center()
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

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.3)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def parent(self):
        parent = super().parent()
        if not parent:
            parent = QApplication.desktop()

        assert isinstance(parent, QWidget)
        return parent

    def center(self):
        geometry = self.frameGeometry()
        parentGeometry = self.parent().geometry()
        geometry.moveCenter(parentGeometry.center())
        self.move(geometry.topLeft())

    def initUserInputHandlers(self):
        self.packagesLoadOptions.reloadButton.clicked.connect(self._reloadButtonClicked)
        self.packagesList.listView.rowActivated.connect(self._packageSelected)

        self.buttonBar.fromApkButton.clicked.connect(self._fromApkButtonClicked)
        self.buttonBar.selectButton.clicked.connect(self._selectButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

        searchInput = self.packagesList.searchInput
        searchInput.returnPressed.connect(self._packageMayBeSelected)
        searchInput.textChanged.connect(self._canSelectPackage)
        searchInput.arrowUpPressed.connect(self._tryFocusPackagesListAndGoUp)
        searchInput.arrowDownPressed.connect(self._tryFocusPackagesListAndGoDown)

        self.packagesLoadOptions.deviceSelectButton.clicked.connect(
            self._selectAnotherDevice
        )

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

    def _canSelectPackage(self):
        canSelect = self.packagesList.canSelectPackage()
        self.buttonBar.selectButton.setEnabled(canSelect)
        return canSelect

    def _packageLoaderSucceeded(self, deviceList: List[str]):
        self._closeLoadingDialog()
        self.buttonBar.fromApkButton.setEnabled(True)
        self._setPackages(deviceList)

        if self._canSelectPackage():
            self._selectDefaultPackage(deviceList)

    def _packageLoaderFailed(self, err: DeviceError):
        self._closeLoadingDialog()
        self.buttonBar.selectButton.setEnabled(False)
        self.buttonBar.fromApkButton.setEnabled(False)
        self.packagesList.setNoData()

        if not isinstance(err, DeviceNotFound):
            msgBoxErr(err.msgBrief, err.msgVerbose)
            return

        msgBrief = "Device not available"
        msgVerbose = "Device is no longer available. Would you like to switch to another device?"  # fmt: skip
        if msgBoxPrompt(msgBrief, msgBrief, msgVerbose):
            self._selectAnotherDevice(True)

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

    def _openLoadingDialog(self):
        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Fetching packages...")
        self._loadingDialog.exec_()

    def _closeLoadingDialog(self):
        self._loadingDialog.close()

    def _startPackageLoader(self):
        deviceSerial = self._appState.lastSelectedDevice.serial
        packageLoader = PackageLoader(self.adbClient(), deviceSerial)
        packageLoader.setStartDelay(500)
        packageLoader.signals.succeeded.connect(self._packageLoaderSucceeded)
        packageLoader.signals.failed.connect(self._packageLoaderFailed)
        QThreadPool.globalInstance().start(packageLoader)

    def adbClient(self):
        return AdbClient(
            self._appState.adb.ipAddr,
            int(self._appState.adb.port),
        )

    def exec_(self):
        self._startPackageListReload()
        return super().exec_()

    def _startPackageListReload(self):
        self._startPackageLoader()
        self._openLoadingDialog()

    def _reloadButtonClicked(self):
        self._startPackageListReload()

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
            msgBoxErr(msgBrief, msgVerbose)
            return

        if self.packagesList.has(packageName):
            self.packagesList.selectPackageByName(packageName)
            self._selectButtonClicked()
            return

        msgBrief = "Package not installed"
        prompt = f"This app is not present on the device. Do you want to install the APK and continue this action?"
        if not msgBoxPrompt(msgBrief, msgBrief, prompt):
            return

        deviceSerial = self._appState.lastSelectedDevice.serial
        action = InstallAppController(self.adbClient())
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
        deviceSelectPane = DeviceSelectDialog(self._appState, self.parent())
        deviceSelectPane.setDeviceAutoSelect(autoSelect)
        result = deviceSelectPane.exec_()
        if result == 0:
            return

        self.packagesList.searchInput.setFocus()
        self._refreshSelectedDevice()
        self._startPackageListReload()
