from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget

from galog.app.app_state import AppState
from galog.app.device.device import AdbClient
from galog.app.ui.base.action import BaseAction
from .task import ShellExecCommand, ShellExecResult, ShellExecTask

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from enum import Enum


class ShellExecAction(BaseAction):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self._setLoadingDialogText("Execute Shell Commands")
        self._adbClient = adbClient

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def executeCommand(self, deviceName: str, command: ShellExecCommand):
        task = ShellExecTask(deviceName, self._adbClient, [command])
        task.signals.succeeded.connect(self._succeeded)
        task.signals.failed.connect(self._failed)
        task.setStartDelay(700)

        QThreadPool.globalInstance().start(task)
        self._execLoadingDialog()

    def executeManyCommands(self, deviceName: str, commands: List[ShellExecCommand]):
        task = ShellExecTask(deviceName, self._adbClient, commands)
        task.signals.succeeded.connect(self._succeeded)
        task.signals.failed.connect(self._failed)
        task.setStartDelay(700)

        QThreadPool.globalInstance().start(task)
        self._execLoadingDialog()
