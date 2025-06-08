from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget
from galog.app.app_state import AppState
from galog.app.device import AdbClient

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr
from ..shell_exec import ShellExecAction, ShellExecCommand

from enum import Enum


class StartAppAction(ShellExecAction):

    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(adbClient, parentWidget)
        self.setLoadingDialogText("Start application")

    def startApp(self, deviceName: str, packageName: str):
        command = ShellExecCommand("Start application", f"monkey -p {packageName} 1")
        self.executeCommand(deviceName, command)
