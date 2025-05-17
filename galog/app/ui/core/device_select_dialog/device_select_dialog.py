from typing import TYPE_CHECKING, List, Optional

from PyQt5.QtCore import QModelIndex, Qt, QThreadPool
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QWidget

from galog.app.app_state import LastSelectedDevice
from galog.app.ui.actions.list_devices.action import ListDevicesAction
from galog.app.ui.base.dialog import BaseDialog
from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.ui.quick_dialogs.loading_dialog import LoadingDialog
from galog.app.device import AdbClient, DeviceInfo
from galog.app.device.device import AdbClient
from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.msgbox import msgBoxErr

from .load_options import DevicesLoadOptions
from .button_bar import ButtonBar
from .device_table import DeviceTable

if TYPE_CHECKING:
    from galog.app.main import AppState
else:
    AppState = object


class DeviceSelectDialog(BaseDialog):
    def __init__(self, appState: AppState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._autoSelect = False
        self._autoSelectDone = False
        self._appState = appState
        self.setWindowTitle("Select Device")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setRelativeGeometry(0.8, 0.6, 900, 600)
        self.setFixedMaxSize(900, 600)
        self.setFixedMinSize(600, 400)
        self.moveToCenter()
        self.initUserInterface()
        self.initUserInputHandlers()
        self.initFocusPolicy()

    def adbClient(self):
        return AdbClient(
            self._appState.adb.ipAddr,
            int(self._appState.adb.port),
        )

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.deviceTable.searchInput.setFocus()
        elif helper.isCtrlRPressed():
            self.devicesLoadOptions.reloadButton.clicked.emit()
        else:
            super().keyPressEvent(event)

    def initUserInputHandlers(self):
        self.devicesLoadOptions.reloadButton.clicked.connect(self._reloadButtonClicked)
        self.deviceTable.tableView.rowActivated.connect(self._deviceSelected)
        self.buttonBar.selectButton.clicked.connect(self._selectButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

        searchInput = self.deviceTable.searchInput
        searchInput.returnPressed.connect(self._deviceMayBeSelected)
        searchInput.textChanged.connect(self._canSelectDevice)
        searchInput.arrowUpPressed.connect(self._tryFocusPackagesListAndGoUp)
        searchInput.arrowDownPressed.connect(self._tryFocusPackagesListAndGoDown)

    def initFocusPolicy(self):
        self.devicesLoadOptions.reloadButton.setFocusPolicy(Qt.NoFocus)
        self.devicesLoadOptions.ipAddressInput.setFocusPolicy(Qt.NoFocus)
        self.devicesLoadOptions.portInput.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.selectButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.NoFocus)

        self.deviceTable.searchInput.setFocus()
        self.setTabOrder(self.deviceTable.searchInput, self.deviceTable.tableView)
        self.setTabOrder(self.deviceTable.tableView, self.deviceTable.searchInput)

    def _canSelectDevice(self):
        canSelect = self.deviceTable.canSelectDevice()
        self.buttonBar.selectButton.setEnabled(canSelect)
        return canSelect

    def initUserInterface(self):
        vBoxLayoutMain = QVBoxLayout()
        self.devicesLoadOptions = DevicesLoadOptions(self)
        vBoxLayoutMain.addWidget(self.devicesLoadOptions)

        self.deviceTable = DeviceTable(self)
        vBoxLayoutMain.addWidget(self.deviceTable)

        self.buttonBar = ButtonBar(self)
        self.buttonBar.selectButton.setEnabled(False)
        vBoxLayoutMain.addWidget(self.buttonBar)

        vBoxLayoutMain.setContentsMargins(0, 0, 0, 0)
        vBoxLayoutMain.setSpacing(0)
        self.setLayout(vBoxLayoutMain)

        self.devicesLoadOptions.setAdbIpAddr(self._appState.adb.ipAddr)
        self.devicesLoadOptions.setAdbPort(str(self._appState.adb.port))

    def _tryFocusPackagesListAndGoUp(self):
        self.deviceTable.trySetFocusAndGoUp()

    def _tryFocusPackagesListAndGoDown(self):
        self.deviceTable.trySetFocusAndGoDown()

    def setDeviceAutoSelect(self, value: bool):
        self._autoSelect = value

    def exec_(self):
        self._refreshDeviceList()
        if self._autoSelect and self._autoSelectDone:
            return DeviceSelectDialog.Accepted

        return super().exec_()

    def _deviceSelected(self, index: Optional[QModelIndex] = None):
        serial, displayName, isValid = self.deviceTable.selectedDevice(index)

        if not isValid:
            msgBrief = "Device is unavailable"
            msgVerbose = "Device can not be selected, because it's unavailable"
            msgBoxErr(msgBrief, msgVerbose, self)
            return

        selectedDevice = LastSelectedDevice(serial, displayName)
        self._appState.lastSelectedDevice = selectedDevice
        self._appState.adb.ipAddr = self.devicesLoadOptions.adbIpAddr()
        self._appState.adb.port = self.devicesLoadOptions.adbPort()
        self.accept()

    def _refreshDeviceList(self):
        action = ListDevicesAction(self.adbClient(), self)
        deviceList = action.listDevices()
        if deviceList is None:
            self._setDevicesEmpty()
            return

        self._setDevices(deviceList)
        if self._canSelectDevice():
            self._selectDefaultDevice(deviceList)

        if self._autoSelect:
            if self.deviceTable.selectTheOnlyOneDevice():
                self._autoSelectDone = True
                self._deviceSelected()

    def _reloadButtonClicked(self):
        self._refreshDeviceList()

    def _selectButtonClicked(self):
        self._deviceSelected()

    def _selectDefaultDevice(self, deviceList: List[DeviceInfo]):
        #
        # Select device which was previously used
        # If device is not present or no device was previously used
        # Select the first one by default
        #

        if self._appState.lastSelectedDevice is not None:
            serial = self._appState.lastSelectedDevice.serial
            if self.deviceTable.selectDeviceBySerial(serial):
                return

        assert len(deviceList) > 0
        serial = deviceList[0].serial
        self.deviceTable.selectDeviceBySerial(serial)

    def _apiLevels(self, device: DeviceInfo):
        hasMin = device.details.sdkVerMin != "<N/A>"
        hasMax = device.details.sdkVerMax != "<N/A>"

        if hasMin and hasMax:
            return f"{device.details.sdkVerMin} - {device.details.sdkVerMax}"

        if not hasMin and not hasMax:
            return "<N/A>"

        if hasMin:
            return device.details.sdkVerMin
        else:
            return device.details.sdkVerMax

    def _addValidDevice(self, device: DeviceInfo):
        self.deviceTable.addValidDevice(
            apiLevels=self._apiLevels(device),
            deviceName=device.details.displayName,
            cpuArch=device.details.cpuArch,
            osInfo=device.details.osInfo,
            deviceSerial=device.serial,
        )

    def _addInvalidDevice(self, device: DeviceInfo):
        errorMessage = f"Device is unavailable ({device.state})"
        self.deviceTable.addInvalidDevice(device.serial, errorMessage)

    def _addDevices(self, devices: List[DeviceInfo]):
        for device in devices:
            if device.details is not None:
                self._addValidDevice(device)
            else:
                self._addInvalidDevice(device)

    def _setDevices(self, devices: List[DeviceInfo]):
        self.buttonBar.selectButton.setEnabled(True)
        self.deviceTable.clear()
        self._addDevices(devices)
        self.deviceTable.sort()

    def _setDevicesEmpty(self):
        self.buttonBar.selectButton.setEnabled(False)
        self.deviceTable.setNoData()

    def _deviceMayBeSelected(self):
        index = self.deviceTable.tableView.currentIndex()
        if not index.isValid():
            return

        self._deviceSelected(index)

    def addTestDevices(self):
        self.deviceTable.addValidDevice(
            "RF8T213A4YW",
            "Google Pixel 4a (sunfish)",
            "Android 13",
            "arm-v64",
            "22-33",
        )

        self.deviceTable.addValidDevice(
            "nm87weerty4",
            "Samsung SM-M127F (X00TD)",
            "Android 12",
            "arm-v64",
            "23-34",
        )

        self.deviceTable.addInvalidDevice(
            "ert45tgf",
            "Device is unavailable (unauthorized)",
        )
