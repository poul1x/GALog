from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QStandardItem, QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QApplication,
    QComboBox,
)
from galog.app.app_state import LastSelectedDevice
from galog.app.components.dialogs.loading_dialog import LoadingDialog
from galog.app.device.device import AdbClient
from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.paths import iconFile

from .adb_server_settings import AdbServerSettings
from .device_table import DeviceTable
from .button_bar import ButtonBar

from typing import List, Optional, Tuple
from zipfile import BadZipFile

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, Qt, QThreadPool
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QFileDialog, QListView

from galog.app.apk_info import APK
from galog.app.components.capture_pane import RunAppAction
from galog.app.components.dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.device.device import AdbDevice, DeviceDetails, DeviceInfo
from galog.app.util.message_box import showErrorMsgBox
from galog.app.util.signals import blockSignals

from .device_loader import DeviceLoader

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from galog.app.main import AppState
else:
    AppState = object


class DeviceSelectPane(QDialog):
    def __init__(self, appState: AppState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._appState = appState
        self.setObjectName("DeviceSelectPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()
        self.initController()
        self.initFocusPolicy()
        self.setGeometryAuto()

    def adbClient(self):
        return AdbClient(
            self._appState.adb.ipAddr,
            int(self._appState.adb.port),
        )

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.deviceTable.searchInput.setFocus()
        else:
            super().keyPressEvent(event)

    def initController(self):
        self.adbServerSettings.reloadButton.clicked.connect(self._reloadButtonClicked)
        self.deviceTable.searchInput.activate.connect(self._deviceMayBeSelected)
        self.deviceTable.tableView.rowActivated.connect(self._deviceSelected)
        self.buttonBar.selectButton.clicked.connect(self._selectButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

    def initFocusPolicy(self):
        self.adbServerSettings.reloadButton.setFocusPolicy(Qt.NoFocus)
        self.adbServerSettings.ipAddressInput.setFocusPolicy(Qt.NoFocus)
        self.adbServerSettings.portInput.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.selectButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.NoFocus)

        self.deviceTable.tableView.setFocus()
        self.setTabOrder(self.deviceTable.searchInput, self.deviceTable.tableView)
        self.setTabOrder(self.deviceTable.tableView, self.deviceTable.searchInput)

    def initUserInterface(self):
        vBoxLayoutMain = QVBoxLayout()
        self.adbServerSettings = AdbServerSettings(self)
        vBoxLayoutMain.addWidget(self.adbServerSettings)

        self.deviceTable = DeviceTable(self)
        vBoxLayoutMain.addWidget(self.deviceTable)

        self.buttonBar = ButtonBar(self)
        self.buttonBar.selectButton.setEnabled(False)
        vBoxLayoutMain.addWidget(self.buttonBar)

        vBoxLayoutMain.setContentsMargins(0, 0, 0, 0)
        vBoxLayoutMain.setSpacing(0)
        self.setLayout(vBoxLayoutMain)

        self.adbServerSettings.setIpAddr(self._appState.adb.ipAddr)
        self.adbServerSettings.setPort(str(self._appState.adb.port))

        # self.searchPane.button.setFocusPolicy(Qt.NoFocus)
        # self.searchPane.input.setFocusPolicy(Qt.NoFocus)
        # self.tableView.setFocusPolicy(Qt.StrongFocus)
        # self.tableView.setFocus()

        # self.setTabOrder(self.tableView, self.searchPane.input)
        # self.setTabOrder(self.searchPane.input, self.tableView)

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.4)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def _showLoadingDialog(self):
        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Connecting to ADB server...")
        self._loadingDialog.exec_()

    def exec_(self):
        self._startDeviceListReload()
        return super().exec_()

    def _deviceSelected(self, index: QModelIndex):
        serial, displayName, isValid = self.deviceTable.selectedDevice(index)

        if isValid:
            selectedDevice = LastSelectedDevice(serial, displayName)
            self._appState.lastSelectedDevice = selectedDevice
            self.accept()
            return

        showErrorMsgBox(
            "Device is unavailable",
            "Device can not be selected, because it's unavailable",
        )

    def _startDeviceLoader(self):
        deviceLoader = DeviceLoader(self.adbClient())
        deviceLoader.setStartDelay(500)
        deviceLoader.signals.succeeded.connect(self._deviceLoaderSucceeded)
        deviceLoader.signals.failed.connect(self._deviceLoaderFailed)
        QThreadPool.globalInstance().start(deviceLoader)

    def _startDeviceListReload(self):
        self._startDeviceLoader()
        self._showLoadingDialog()

    def _reloadButtonClicked(self):
        self._appState.adb.ipAddr = self.adbServerSettings.ipAddr()
        self._appState.adb.port = self.adbServerSettings.port()
        self._startDeviceListReload()

    def _selectButtonClicked(self):
        self._deviceSelected(self.deviceTable.tableView.currentIndex())

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

    def _deviceLoaderSucceeded(self, deviceList: List[DeviceInfo]):
        self._loadingDialog.close()
        self._setDevices(deviceList)
        self._selectDefaultDevice(deviceList)

    def _deviceLoaderFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        self._setDevicesEmpty()
        showErrorMsgBox(msgBrief, msgVerbose)

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
        with blockSignals(self.deviceTable):  # TODO: why I need this
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
