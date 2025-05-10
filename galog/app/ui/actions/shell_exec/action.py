from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QFileDialog

from galog.app.app_state import AppState
from galog.app.device.device import AdbClient
from galog.app.ui.base.action import BaseAction
from .task import ShellExecCommand, ShellExecTask

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from enum import Enum

class ShellExecAction(BaseAction):
    def __init__(self, adbClient: AdbClient):
        super().__init__()
        self._setLoadingDialogText("Execute Shell Commands")
        self._adbClient = adbClient

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def executeCommand(self, deviceName: str, command: ShellExecCommand):
        task = ShellExecTask(deviceName, self._adbClient, [command])
        task.signals.succeeded.connect(self._succeeded)
        task.signals.failed.connect(self._failed)
        task.setStartDelay(700)

        QThreadPool.globalInstance().start(task)
        self._loadingDialog.exec_()

    def executeManyCommands(self, deviceName: str, commands: List[ShellExecCommand]):
        task = ShellExecTask(deviceName, self._adbClient, commands)
        task.signals.succeeded.connect(self._succeeded)
        task.signals.failed.connect(self._failed)
        task.setStartDelay(700)

        QThreadPool.globalInstance().start(task)
        self._loadingDialog.exec_()
