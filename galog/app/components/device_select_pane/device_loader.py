from typing import Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.device import AdbClient
from galog.app.device.device import deviceListWithInfo
from galog.app.device.errors import DeviceError


class DeviceLoaderSignals(QObject):
    succeeded = pyqtSignal(list)
    failed = pyqtSignal(str, str)


class DeviceLoader(QRunnable):
    _client: AdbClient
    _msDelay: Optional[int]

    def __init__(self, client: AdbClient):
        super().__init__()
        self.signals = DeviceLoaderSignals()
        self._client = client
        self._msDelay = None

    def _getDevices(self):
        return deviceListWithInfo(self._client)

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def run(self):
        try:
            self._delayIfNeeded()
            devices = self._getDevices()
            self.signals.succeeded.emit(devices)

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
