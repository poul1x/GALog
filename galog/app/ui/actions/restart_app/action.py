from galog.app.device import AdbClient

from ..shell_exec import ShellExecAction, ShellExecCommand


class RestartAppAction(ShellExecAction):
    def __init__(self, adbClient: AdbClient):
        super().__init__(adbClient)
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
