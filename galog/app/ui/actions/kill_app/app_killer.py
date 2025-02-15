from typing import Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.errors import DeviceError


class AppKillerSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class AppKiller(QRunnable):
    _client: AdbClient
    _msDelay: Optional[int]

    def __init__(self, client: AdbClient, deviceName: str, packageName: str):
        super().__init__()
        self.signals = AppKillerSignals()
        self._deviceName = deviceName
        self._packageName = packageName
        self._client = client
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _execKillApp(self):
        with deviceRestricted(self._client, self._deviceName) as device:
            device.shell(f"am force-stop {self._packageName}")

    def run(self):
        try:
            self._delayIfNeeded()
            self._execKillApp()
            self.signals.succeeded.emit()

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
