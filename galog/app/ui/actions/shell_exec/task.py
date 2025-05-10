from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from io import TextIOWrapper
from typing import IO, Callable, List, Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal
from galog.app.app_state import AppState

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device import AdbDevice
from galog.app.device.errors import DeviceError

from galog.app.ui.base.task import BaseTask

from typing import Callable

ShellExecVerifier = Callable[[int, str], bool]


@dataclass
class ShellExecCommand:
    name: str
    cmdString: str
    verifier: ShellExecVerifier = lambda code, output: code == 0


@dataclass
class ShellExecResult:
    command: ShellExecCommand
    succeeded: bool
    exitCode: bool
    output: str


class CommandFailed(Exception):
    def __init__(self, shellExecResult: ShellExecResult) -> None:
        super().__init__(shellExecResult)

    def shellExecResult(self):
        return self.args[0]


class ShellExecTaskSignals(QObject):
    succeeded = pyqtSignal()
    commandFailed = pyqtSignal(ShellExecResult)
    failed = pyqtSignal(str, str)


class ShellExecTask(BaseTask):
    def __init__(
        self,
        deviceName: str,
        adbClient: AdbClient,
        cmdList: List[ShellExecCommand],
    ):
        super().__init__()
        self.signals = ShellExecTaskSignals()
        self._cmdList = cmdList
        self._adbClient = adbClient
        self._deviceName = deviceName

    def _execCommand(self, device: AdbDevice, command: ShellExecCommand):
        output = device.shell(command.cmdString)
        exitCode = int(device.shell("echo $?"))
        success = command.verifier(exitCode, output)
        return ShellExecResult(command, success, exitCode, output)

    def _execCommandList(self):
        with deviceRestricted(self._adbClient, self._deviceName) as device:
            for command in self._cmdList:
                result = self._execCommand(device, command)
                if not result.succeeded:
                    raise CommandFailed(result)

    def entrypoint(self):
        try:
            self._execCommandList()
        except CommandFailed as e:
            self.signals.commandFailed.emit(e.shellExecResult())
        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
        except Exception:
            msgBrief = "Unknown error"
            msgVerbose = "Unknown Error - Possibly a bug in the application"
            self.signals.failed.emit(msgBrief, msgVerbose)
            raise
        else:
            self.signals.succeeded.emit()
