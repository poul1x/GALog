from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget
from galog.app.app_state import AppState
from galog.app.device import AdbClient
from galog.app.device import DeviceInfo
from galog.app.device.errors import DeviceError, DeviceNotFound
from galog.app.ui.actions.list_devices.task import ListDevicesTask
from galog.app.ui.base.action import BaseAction

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from ..shell_exec import ShellExecAction, ShellExecCommand
from .task import ListPackagesTask

class ListPackagesAction(BaseAction):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self.setLoadingDialogText("Fetching packages...")
        self._allowSelectAnotherDevice = False
        self._needSelectAnotherDevice = False
        self._adbClient = adbClient
        self._packagesList = []

    def _packageFound(self, packageName: str):
        self._packagesList.append(packageName)

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, e: DeviceError):
        self._setFailed()
        if isinstance(e, DeviceNotFound) and self._allowSelectAnotherDevice:
            msgBrief = "Device not available"
            msgVerbose = "Selected device is no longer available. Would you like to switch to another device?"  # fmt: skip
            self._needSelectAnotherDevice = self._msgBoxPrompt(msgBrief, msgVerbose)
            return

        self._msgBoxErr(e.msgBrief, e.msgVerbose)


    def listPackages(self, deviceSerial: str):
        task = ListPackagesTask(deviceSerial, self._adbClient)
        task.setStartDelay(500)
        task.signals.succeeded.connect(self._succeeded)
        task.signals.packageFound.connect(self._packageFound)
        task.signals.failed.connect(self._failed)

        QThreadPool.globalInstance().start(task)
        self._execLoadingDialog()

        if self.succeeded():
            return self._packagesList
        else:
            return None

    def setAllowSelectAnotherDevice(self, allow: bool):
        self._allowSelectAnotherDevice = allow

    def allowSelectAnotherDevice(self):
        return self._allowSelectAnotherDevice

    def needSelectAnotherDevice(self):
        return self._needSelectAnotherDevice
