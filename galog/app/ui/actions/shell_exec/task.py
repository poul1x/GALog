from dataclasses import dataclass
from typing import Callable, List

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from galog.app.device import AdbClient, AdbDevice, deviceRestricted
from galog.app.device.errors import DeviceError
from galog.app.ui.base.task import Task

ShellExecVerifier = Callable[[str, str], bool]
_DEFAULT_VERIFIER = lambda code, output: code == "0"


@dataclass
class ShellExecCommand:
    name: str
    cmdString: str
    verifier: ShellExecVerifier = _DEFAULT_VERIFIER
    waitTimeMs: int = 0


@dataclass
class ShellExecResult:
    command: ShellExecCommand
    succeeded: bool
    exitCode: str
    output: str


class CommandFailed(Exception):
    def __init__(self, shellExecResult: ShellExecResult) -> None:
        super().__init__(shellExecResult)

    def shellExecResult(self) -> ShellExecResult:
        return self.args[0]

    def __str__(self) -> str:
        execResult = self.shellExecResult()
        return "ShellExec failed: " + ", ".join(
            [
                f"Name='{execResult.command.name}'",
                f"CMDString='{execResult.command.cmdString}'",
                f"ExitCode='{execResult.exitCode}'",
                f"Output='{execResult.output}'",
            ]
        )


class ShellExecTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)
    cmdSucceeded = pyqtSignal(ShellExecResult)
    cmdFailed = pyqtSignal(ShellExecResult)


class ShellExecTask(Task):
    def __init__(
        self,
        deviceName: str,
        cmdList: List[ShellExecCommand],
        adbClient: AdbClient,
    ):
        super().__init__()
        self.signals = ShellExecTaskSignals()
        self._cmdList = cmdList
        self._adbClient = adbClient
        self._deviceName = deviceName

    def _execCommand(self, device: AdbDevice, command: ShellExecCommand):
        combinedOutput: str = device.shell(command.cmdString + '; echo -e "\n$?"')
        output, exitCode = combinedOutput.rstrip().rsplit("\n", 1)
        self._logger.debug("Execute command: '%s'", str(command))
        self._logger.debug("Result: exitCode='%s' output='%s'", exitCode, output)
        succeeded = command.verifier(exitCode, output)
        return ShellExecResult(command, succeeded, exitCode, output)

    def _execCommandList(self):
        with deviceRestricted(self._deviceName, self._adbClient) as device:
            for command in self._cmdList:
                result = self._execCommand(device, command)
                if not result.succeeded:
                    self.signals.cmdFailed.emit(result)
                    raise CommandFailed(result)

                if command.waitTimeMs > 0:
                    QThread.msleep(command.waitTimeMs)

                self.signals.cmdSucceeded.emit(result)

    def _shellExecErrorString(self, execResult: ShellExecResult):
        return (
            "Shell command failed",
            f"Shell command '{execResult.command.name}' failed with exit code '{execResult.exitCode}'",
        )

    def entrypoint(self):
        try:
            self._execCommandList()
        except CommandFailed as e:
            self._logger.error(str(e))
            msgBrief, msgVerbose = self._shellExecErrorString(e.shellExecResult())
            self.signals.failed.emit(msgBrief, msgVerbose)
        except DeviceError as e:
            self._logger.error(str(e))
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
        except Exception:
            self._logger.exception("Got unknown error:")
            msgBrief = "Unknown error"
            msgVerbose = "Unknown Error - Possibly a bug in the application"
            self.signals.failed.emit(msgBrief, msgVerbose)
        else:
            self.signals.succeeded.emit()
