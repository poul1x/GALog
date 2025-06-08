from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget

from galog.app.app_state import AppState
from galog.app.device.device import AdbClient
from galog.app.ui.base.action import Action
from .task import ShellExecCommand, ShellExecResult, ShellExecTask

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from enum import Enum


class ShellExecAction(Action):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self.setLoadingDialogText("Execute Shell Commands")
        self._adbClient = adbClient

    def _succeeded(self):
        self._setSucceeded()

    def _cmdSucceeded(self, result: ShellExecResult):
        self._logger.info(f"Command succeeded: {result}")

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def _cmdFailed(self, result: ShellExecResult):
        self._logger.warning(f"Command failed: {result}")

    def executeCommand(
        self,
        deviceName: str,
        command: ShellExecCommand,
        delay: int = 700,
    ):
        task = ShellExecTask(deviceName, [command], self._adbClient)
        task.signals.cmdSucceeded.connect(self._cmdSucceeded)
        task.signals.succeeded.connect(self._succeeded)
        task.signals.cmdFailed.connect(self._cmdFailed)
        task.signals.failed.connect(self._failed)
        task.setStartDelay(delay)

        QThreadPool.globalInstance().start(task)
        self._execLoadingDialog()

    def executeManyCommands(
        self,
        deviceName: str,
        commands: List[ShellExecCommand],
        delay: int = 700,
    ):
        task = ShellExecTask(deviceName, commands, self._adbClient)
        task.signals.succeeded.connect(self._succeeded)
        task.signals.failed.connect(self._failed)
        task.setStartDelay(delay)

        QThreadPool.globalInstance().start(task)
        self._execLoadingDialog()
