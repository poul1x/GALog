from galog.app.device import AdbClient
from PyQt5.QtWidgets import QWidget

from ..shell_exec import ShellExecAction, ShellExecCommand


class RestartAppAction(ShellExecAction):
    def __init__(self, adbClient: AdbClient, parentWidget: QWidget):
        super().__init__(adbClient, parentWidget)
        self.setLoadingDialogText("Restart application")

    def restartApp(self, deviceName: str, packageName: str):
        commands = [
            ShellExecCommand(
                "Stop application",
                f"am force-stop {packageName}",
                waitTimeMs=100,
            ),
            ShellExecCommand(
                "Start application",
                f"monkey -p {packageName} 1",
            ),
        ]

        self.executeManyCommands(deviceName, commands)
