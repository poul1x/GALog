from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget
from galog.app.app_state import AppState
from galog.app.device import AdbClient
from galog.app.ui.actions.shell_exec.task import ShellExecResult

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr
from ..shell_exec import ShellExecAction, ShellExecCommand

from enum import Enum


class GetAppPidsAction(ShellExecAction):

    _CMD_NAME = "Get App PIDs"

    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(adbClient, parentWidget)
        self.setLoadingDialogText("Getting App PIDs")
        self._app_pids = None

    def _cmdSucceeded(self, result: ShellExecResult):
        super()._cmdSucceeded(result)
        assert result.command.name == self._CMD_NAME
        self._app_pids = list(set(result.output.split()))

    def appPids(self, deviceName: str, packageName: str):
        command = ShellExecCommand(self._CMD_NAME, f"pidof {packageName}")
        self.executeCommand(deviceName, command)
        return self._app_pids
