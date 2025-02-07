from contextlib import suppress
from typing import List, Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.errors import DeviceError


class PackageLoaderSignals(QObject):
    succeeded = pyqtSignal(list)
    failed = pyqtSignal(str, str)


class PackageLoader(QRunnable):
    _client: AdbClient
    _msDelay: Optional[int]

    def __init__(self, client: AdbClient, deviceSerial: str):
        super().__init__()
        self.signals = PackageLoaderSignals()
        self._deviceSerial = deviceSerial
        self._client = client
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _getPackages(self):
        with deviceRestricted(self._client, self._deviceSerial) as device:
            packages = device.list_packages()

        return packages

    def run(self):
        try:
            self._delayIfNeeded()
            packages = self._getPackages()
            self.signals.succeeded.emit(packages)

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
