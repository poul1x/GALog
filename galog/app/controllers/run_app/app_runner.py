from typing import Optional

from PyQt5.QtCore import pyqtSignal, QThread, QObject,QRunnable
from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.errors import DeviceError


class AppRunnerSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class AppRunner(QRunnable):
    _client: AdbClient
    _msDelay: Optional[int]

    def __init__(self, client: AdbClient, deviceName: str, packageName: str):
        super().__init__()
        self.signals = AppRunnerSignals()
        self._deviceName = deviceName
        self._packageName = packageName
        self._client = client
        self._appDebug = False
        self._msDelay = None

    def setAppDebug(self, debug: bool):
        self._appDebug = debug

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _execRunApp(self):
        with deviceRestricted(self._client, self._deviceName) as device:
            waitDebugOpt = "--wait-dbg" if self._appDebug else ""
            device.shell(f"monkey {waitDebugOpt} -p {self._packageName} 1")

    def run(self):
        try:
            self._delayIfNeeded()
            self._execRunApp()
            self.signals.succeeded.emit()

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
