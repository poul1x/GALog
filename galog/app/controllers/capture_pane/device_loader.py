from contextlib import suppress
from typing import List, Optional

from PySide6.QtCore import QObject, QRunnable, QThread, Signal

from galog.app.device import AdbClient, devicesRestricted
from galog.app.device.errors import DeviceError


class DeviceLoaderSignals(QObject):
    succeeded = Signal(list, str)
    failed = Signal(str, str)


class DeviceLoader(QRunnable):
    _client: AdbClient
    _lastSelectedDevice: Optional[str]
    _msDelay: Optional[int]

    def __init__(self, client: AdbClient, lastSelectedDevice: Optional[str] = None):
        super().__init__()
        self.signals = DeviceLoaderSignals()
        self._lastSelectedDevice = lastSelectedDevice
        self._client = client
        self._msDelay = None

    def _getDevices(self):
        return [dev.serial for dev in devicesRestricted(self._client)]

    def _selectDevice(self, devices: List[str]):
        i = 0
        with suppress(ValueError):
            i = devices.index(self._lastSelectedDevice)

        return devices[i]

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def run(self):
        try:
            self._delayIfNeeded()
            devices = self._getDevices()
            device = self._selectDevice(devices)
            self.signals.succeeded.emit(devices, device)

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
