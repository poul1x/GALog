from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from distutils.log import fatal
from importlib.resources import Package
from msilib.schema import Error
import os
from pydoc import cli
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yaml

from galog.app.device import AdbClient, AdbDevice, devicesRestricted
from galog.app.device.errors import DeviceError, DeviceNotFound, DeviceStateInvalid

from ...components.capture_pane import CapturePane
from galog.app.highlighting import HighlightingRules
from galog.app.components.message_view_pane import LogMessageViewPane

class DeviceLoaderSignals(QObject):
    succeeded = pyqtSignal(list, str)
    failed = pyqtSignal(str, str)

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