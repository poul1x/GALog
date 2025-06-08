from typing import Optional

from PyQt5.QtWidgets import QWidget

from galog.app.device import AdbClient

from ..shell_exec import ShellExecAction, ShellExecCommand


class StartAppAction(ShellExecAction):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(adbClient, parentWidget)
        self.setLoadingDialogText("Start application")

    def startApp(self, deviceName: str, packageName: str):
        command = ShellExecCommand("Start application", f"monkey -p {packageName} 1")
        self.executeCommand(deviceName, command)
