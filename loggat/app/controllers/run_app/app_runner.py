import re
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from loggat.app.device import AdbClient, AdbDevice, deviceRestricted
from loggat.app.device.errors import DeviceError

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
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _execRunApp(self):
        with deviceRestricted(self._client, self._deviceName) as device:
            device.shell(f"monkey -p {self._packageName} 1")

    def run(self):
        try:
            self._delayIfNeeded()
            self._execRunApp()
            self.signals.succeeded.emit()

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)