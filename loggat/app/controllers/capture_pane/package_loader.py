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

from pyaxmlparser import APK
from loggat.app.components.error_dialog import ErrorDialog

from loggat.app.components.loading_dialog import LoadingDialog

from loggat.app.device import AdbClient, AdbDevice
from loggat.app.device.errors import (
    DeviceError,
    DeviceNotFound,
    DeviceStateInvalid,
    ErrorType,
)

from ...components.capture_pane import CapturePane
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane


class PackageLoaderSignals(QObject):
    succeeded = pyqtSignal(list, str)
    failed = pyqtSignal(ErrorType, str, str)


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
        with self._client.deviceRestricted(self._deviceName) as device:
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

        except DeviceStateInvalid as e:
            self.signals.failed.emit(e.errorType, e.deviceName, e.deviceState)

        except DeviceNotFound as e:
            self.signals.failed.emit(e.errorType, e.deviceName, None)

        except DeviceError as e:
            self.signals.failed.emit(e.errorType, None, None)
