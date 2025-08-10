from ipaddress import IPv4Address
from typing import List, Optional

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from galog.app.device import DeviceInfo
from galog.app.device.device import AdbClient
from galog.app.msgbox import msgBoxErr
from galog.app.settings.models import LastSelectedDevice
from galog.app.settings.settings import readSettings, writeSettings
from galog.app.ui.actions.list_devices.action import ListDevicesAction
from galog.app.ui.base.dialog import Dialog
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from .button_bar import BottomButtonBar
from .device_table import DeviceTable
from .load_options import DevicesLoadOptions


class DeviceSelectDialog(Dialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = readSettings()
        self._autoSelect = False
        self._autoSelectDone = False
        self.setWindowTitle("Select Device")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setRelativeGeometry(0.8, 0.6, 900, 600)
        self.setFixedMaxSize(900, 600)
        self.setFixedMinSize(600, 400)
        self.moveToCenter()
        self.initUserInterface()
        self.initUserInputHandlers()
        self.initFocusPolicy()

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
        self.buttonBar.selectButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.ClickFocus)
        self.devicesLoadOptions.ipAddressInput.setFocusPolicy(Qt.ClickFocus)
        self.devicesLoadOptions.portInput.setFocusPolicy(Qt.ClickFocus)

        self.setTabOrder(self.deviceTable.searchInput, self.deviceTable.tableView)
        self.setTabOrder(self.deviceTable.tableView, self.deviceTable.searchInput)
        self.setTabOrder(self.devicesLoadOptions.ipAddressInput, self.devicesLoadOptions.portInput)  # fmt: skip
        self.setTabOrder(self.devicesLoadOptions.portInput, self.deviceTable.tableView)
        self.deviceTable.searchInput.setFocus()

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

        self.buttonBar = BottomButtonBar(self)
        self.buttonBar.selectButton.setEnabled(False)
        vBoxLayoutMain.addWidget(self.buttonBar)

        vBoxLayoutMain.setContentsMargins(0, 0, 0, 0)
        vBoxLayoutMain.setSpacing(0)
        self.setLayout(vBoxLayoutMain)

        self.devicesLoadOptions.setAdbIpAddr(str(self._settings.adbServer.ipAddr))
        self.devicesLoadOptions.setAdbPort(str(self._settings.adbServer.port))

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

        self._settings.adbServer.ipAddr = IPv4Address(self.devicesLoadOptions.adbIpAddr())
        self._settings.adbServer.port = int(self.devicesLoadOptions.adbPort())
        selectedDevice = LastSelectedDevice.new(serial, displayName)
        self._settings.lastSelectedDevice = selectedDevice
        writeSettings(self._settings)
        self.accept()

    def _refreshDeviceList(self):
        ipAddr = self.devicesLoadOptions.adbIpAddr()
        port = int(self.devicesLoadOptions.adbPort())
        client = AdbClient(ipAddr, port)

        action = ListDevicesAction(client, self)
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

        if self._settings.lastSelectedDevice is not None:
            serial = self._settings.lastSelectedDevice.serial
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
