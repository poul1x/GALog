from typing import Optional

from PyQt5.QtWidgets import QWidget

from galog.app.device import AdbClient

from ..shell_exec import ShellExecAction, ShellExecCommand


class StopAppAction(ShellExecAction):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(adbClient, parentWidget)
        self.setLoadingDialogText("Stop application")

    def stopApp(self, deviceName: str, packageName: str):
        command = ShellExecCommand("Stop application", f"am force-stop {packageName}")
        self.executeCommand(deviceName, command)
