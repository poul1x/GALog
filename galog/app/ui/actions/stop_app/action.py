from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QFileDialog
from galog.app.app_state import AppState
from galog.app.device import AdbClient

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr
from ..shell_exec import ShellExecAction, ShellExecCommand

from enum import Enum


class StopAppAction(ShellExecAction):
    def __init__(self, adbClient: AdbClient):
        super().__init__(adbClient)
        self._setLoadingDialogText("Stop application")

    def stopApp(self, deviceName: str, packageName: str):
        command = ShellExecCommand("Stop application", f"am force-stop {packageName}")
        self.executeCommand(deviceName, command)
