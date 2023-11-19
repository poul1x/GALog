from contextlib import suppress
from typing import List, Optional

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.errors import DeviceError


class PackageLoaderSignals(QObject):
    succeeded = pyqtSignal(list, str)
    failed = pyqtSignal(str, str)


class PackageLoader(QRunnable):
    _client: AdbClient
    _lastSelectedPackage: str
    _msDelay: Optional[int]

    def __init__(
        self,
        client: AdbClient,
        deviceName: str,
        lastSelectedPackage: Optional[str] = None,
    ):
        super().__init__()
        self.signals = PackageLoaderSignals()
        self._lastSelectedPackage = lastSelectedPackage
        self._deviceName = deviceName
        self._client = client
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _getPackages(self):
        with deviceRestricted(self._client, self._deviceName) as device:
            packages = device.list_packages()

        return packages

    def _selectPackage(self, packages: List[str]):
        i = 0
        with suppress(ValueError):
            i = packages.index(self._lastSelectedPackage)

        return packages[i]

    def run(self):
        try:
            self._delayIfNeeded()
            packages = self._getPackages()
            package = self._selectPackage(packages)
            self.signals.succeeded.emit(packages, package)

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
