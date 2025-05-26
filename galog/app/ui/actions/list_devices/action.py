from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget
from galog.app.app_state import AppState
from galog.app.device import AdbClient
from galog.app.device import DeviceInfo
from galog.app.ui.actions.list_devices.task import ListDevicesTask
from galog.app.ui.base.action import BaseAction

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr
from ..shell_exec import ShellExecAction, ShellExecCommand

class ListDevicesAction(BaseAction):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self.setLoadingDialogText("Loading device list...")
        self._client = adbClient
        self._deviceList = []

    def _deviceFound(self, deviceInfo: DeviceInfo):
        self._deviceList.append(deviceInfo)

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def listDevices(self):
        task = ListDevicesTask(self._client)
        task.setStartDelay(500)
        task.signals.succeeded.connect(self._succeeded)
        task.signals.deviceFound.connect(self._deviceFound)
        task.signals.failed.connect(self._failed)

        QThreadPool.globalInstance().start(task)
        self._execLoadingDialog()

        if self.succeeded():
            return self._deviceList
        else:
            return None