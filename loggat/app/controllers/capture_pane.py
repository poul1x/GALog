from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from distutils.log import fatal
from enum import Enum, auto
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

from loggat.app.controllers.loading_dialog import LoadingDialog
from ..components.capture_pane import CapturePane
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane

from loggat.app.logcat import (
    AndroidAppLogReader,
    AndroidLogReader,
    LogcatLine,
    ProcessEndedEvent,
    ProcessStartedEvent,
)
from loggat.app.mtsearch import SearchItem, SearchItemTask, SearchResult
from loggat.app.util.paths import HIGHLIGHTING_RULES_FILE, STYLES_DIR

from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice


class ErrorType(int, Enum):
    ConnectionFailure = auto()
    NoDevicesFound = auto()
    DeviceNotFound = auto()
    DeviceStateInvalid = auto()


@dataclass
class AdbDeviceInfo:
    name: str
    state: str


DEVICE_STATE_OK = "device"


class BaseError(Exception):
    def __init__(self, errorType: ErrorType, *args):
        super().__init__(errorType, *args)

    @property
    def errorType(self):
        return self.args[0]


class DeviceStateInvalid(BaseError):
    def __init__(self, deviceState: str):
        super().__init__(ErrorType.DeviceStateInvalid, deviceState)

    @property
    def deviceState(self):
        return self.args[1]


class DeviceLoaderError(BaseError):
    pass


class PackageLoaderError(BaseError):
    pass


class DeviceLoader(QObject):
    def __init__(self, client: AdbClient, lastSelectedDevice: Optional[str] = None):
        super().__init__()
        self._lastSelectedDevice = lastSelectedDevice
        self._client = client

    exited = pyqtSignal()
    succeeded = pyqtSignal(list, AdbDeviceInfo)
    failed = pyqtSignal(ErrorType)

    def _getDevices(self):
        result: List[AdbDeviceInfo] = []

        try:
            device: AdbDevice
            for device in self._client.devices():
                devInfo = AdbDeviceInfo(device.serial, device.get_state())
                result.append(devInfo)

        except RuntimeError:
            raise DeviceLoaderError(ErrorType.ConnectionFailure)

        if len(result) == 0:
            raise DeviceLoaderError(ErrorType.NoDevicesFound)

        return result

    def _selectDevice(self, devices: List[AdbDeviceInfo]):
        result = devices[0]
        for device in devices:
            if device.name == self._lastSelectedDevice:
                result = device.name

        return result

    def run(self):
        try:
            devices = self._getDevices()
            device = self._selectDevice(devices)
            self.succeeded.emit(devices, device)

        except DeviceLoaderError as e:
            self.failed.emit(e.errorType)

        self.exited.emit()


class PackageLoader(QObject):
    _lastSelectedPackage: str
    _client: AdbClient

    succeeded = pyqtSignal(list)
    failed = pyqtSignal(ErrorType, str)

    def __init__(
        self,
        client: AdbClient,
        deviceName: str,
        lastSelectedPackage: Optional[str] = None,
    ):
        super().__init__()
        self._lastSelectedPackage = lastSelectedPackage
        self._deviceName = deviceName
        self._client = client

    def _getPackages(self):
        try:
            device: AdbDevice = self._client.device(self._deviceName)
            if not device:
                raise PackageLoaderError(ErrorType.DeviceNotFound)

            state = device.get_state()
            if state != DEVICE_STATE_OK:
                raise DeviceStateInvalid(state)

            packages = device.list_packages()

        except RuntimeError:
            raise PackageLoaderError(ErrorType.ConnectionFailure)

        return packages

    def _selectPackage(self, packages: List[str]):
        i = 0
        with suppress(ValueError):
            i = packages.index(self._lastSelectedPackage)

        return packages[i]

    def run(self):
        try:
            packages = self._getPackages()
            package = self._selectPackage(packages)
            self.succeeded.emit(packages, package)

        except DeviceStateInvalid as e:
            self.failed.emit(e.errorType, e.deviceState)

        except PackageLoaderError as e:
            self.failed.emit(e.errorType, None)


class CapturePaneController:
    _capturePane: Optional[CapturePane]

    def __init__(self, adb_host: str, adb_port: int) -> None:
        self._client = AdbClient(adb_host, adb_port)
        self._lastSelectedDevice = None
        self._lastSelectedPackage = None
        self._capturePane = None

    def getSelectedDevice(self):
        assert self.selectedDevice is not None
        return self.selectedDevice

    def getSelectedPackage(self):
        assert self.selectedPackage is not None
        return self.selectedPackage

    def captureTargetSelected(self):
        return self.selectedPackage is not None and self.selectedAdbDevice is not None

    def setWidget(self, capturePane: CapturePane) -> None:
        self._capturePane = capturePane
        self._capturePane.deviceChanged.connect(self.deviceChanged)
        self._capturePane.packageSelected.connect(self.packageSelected)

    def packageSelected(self, packageName: str):
        self.selectedPackage = packageName

    def deviceChanged(self, deviceName: str):
        self.selectedAdbDevice = deviceName

    def deviceLoaderSucceded(
        self, deviceList: List[AdbDeviceInfo], selectedDevice: AdbDeviceInfo
    ):
        for device in deviceList:
            self._capturePane.addDevice(device.name, device.state)

        self._capturePane.setSelectedDevice(selectedDevice.name)

    def deviceLoaderFailed(self, errorType: ErrorType):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Error")
        error_msg.setText("An error occurred.")
        error_msg.setInformativeText("This is an example of an error message.")
        error_msg.setStandardButtons(QMessageBox.Ok)
        print("AAAA")

    def deviceLoaderThreadExited(self):
        print("BBB")
        self.dialog.close()
        self.thread.quit()
        self.thread.wait()

    def newCaptureDialog(self):
        self.thread = QThread()
        self.deviceLoader = DeviceLoader(self._client)
        self.deviceLoader.succeeded.connect(self.deviceLoaderSucceded)
        self.deviceLoader.failed.connect(self.deviceLoaderFailed)
        self.deviceLoader.moveToThread(self.thread)
        self.thread.started.connect(self.deviceLoader.run)
        self.deviceLoader.exited.connect(self.deviceLoaderThreadExited)

        QTimer.singleShot(1000, self.thread.start)
        self.dialog = LoadingDialog()
        self.dialog.exec_()

        self._capturePane.exec_()
