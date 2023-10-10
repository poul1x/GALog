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

from loggat.app.components.loading_dialog import LoadingDialog
from ..components.capture_pane import CapturePane
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane

from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice


class ErrorType(int, Enum):
    ConnectionFailure = auto()
    NoDevicesFound = auto()
    DeviceNotFound = auto()
    DeviceStateInvalid = auto()


DEVICE_STATE_OK = "device"


class BaseError(Exception):
    def __init__(self, errorType: ErrorType, *args):
        super().__init__(errorType, *args)

    @property
    def errorType(self):
        return self.args[0]


class AdbConnectionError(BaseError):
    def __init__(self):
        super().__init__(ErrorType.ConnectionFailure)


class NoDevicesFound(BaseError):
    def __init__(self):
        super().__init__(ErrorType.NoDevicesFound)


class DeviceStateInvalid(BaseError):
    def __init__(self, deviceName: str, deviceState: str):
        super().__init__(ErrorType.DeviceStateInvalid, deviceName, deviceState)

    @property
    def deviceName(self):
        return self.args[1]

    @property
    def deviceState(self):
        return self.args[2]


class DeviceNotFound(BaseError):
    def __init__(self, deviceName: str):
        super().__init__(ErrorType.DeviceNotFound, deviceName)

    @property
    def deviceName(self):
        return self.args[1]


class DeviceLoaderSignals(QObject):
    succeeded = pyqtSignal(list, str)
    failed = pyqtSignal(ErrorType)


class PackageLoaderSignals(QObject):
    succeeded = pyqtSignal(list, str)
    failed = pyqtSignal(ErrorType, str, str)


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
        try:
            devices: List[AdbDevice] = self._client.devices()
        except RuntimeError:
            raise AdbConnectionError()

        if len(devices) == 0:
            raise NoDevicesFound()

        return [dev.serial for dev in devices]

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

        except BaseError as e:
            self.signals.failed.emit(e.errorType)


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

    def _ppadbDeviceMonkeyPatch(self, deviceName: str):
        class MyAdbDevice(AdbDevice):
            def __init__(self, client, serial, state):
                super().__init__(client, serial)
                self.state = state

        cmd = "host:devices"
        result: str = self._client._execute_cmd(cmd)
        if not result:
            return None

        for line in result.strip().split("\n"):
            serial, state = line.split()
            if serial == deviceName:
                return MyAdbDevice(self._client, serial, state)

        return None

    def _getPackages(self):
        try:
            #
            # XXX: Now ppadb does not save the device status
            #      in client.devices() and device.get_state() raises
            #      RuntimeError, so there's no way to get status via
            #      public API. So, I had to create a monkey patch for this
            #
            # device: AdbDevice = self._client.device(self._deviceName)
            # if not device:
            #     raise PackageLoaderError(ErrorType.DeviceNotFound)
            # state = device.get_state()
            #

            device = self._ppadbDeviceMonkeyPatch(self._deviceName)
            if not device:
                raise DeviceNotFound(self._deviceName)

            if device.state != DEVICE_STATE_OK:
                raise DeviceStateInvalid(device.serial, device.state)

            packages = device.list_packages()

        except RuntimeError:
            raise AdbConnectionError()

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

        except BaseError as e:
            self.signals.failed.emit(e.errorType, None, None)


class CapturePaneController:
    _capturePane: Optional[CapturePane]

    def __init__(self, adb_host: str, adb_port: int) -> None:
        self._client = AdbClient(adb_host, adb_port)
        self._lastSelectedDevice = None
        self._lastSelectedPackage = None
        self._nothingSelected = False
        self._capturePane = None

    def selectedDevice(self):
        return self._lastSelectedDevice

    def selectedPackage(self):
        return self._lastSelectedPackage

    def captureTargetSelected(self):
        return (
            self._nothingSelected == False
            and self._lastSelectedDevice is not None
            and self._lastSelectedPackage is not None
        )

    def setWidget(self, capturePane: CapturePane) -> None:
        self._capturePane = capturePane
        self._capturePane.deviceChanged.connect(self.deviceChanged)
        self._capturePane.packageSelected.connect(self.packageSelected)
        self._capturePane.rejected.connect(self.nothingSelected)
        self._nothingSelected = False

    def nothingSelected(self):
        self._nothingSelected = True

    def packageSelected(self, packageName: str):
        self._lastSelectedPackage = packageName

    def deviceChanged(self, deviceName: str):
        self._lastSelectedDevice = deviceName
        self._capturePane.clearPackages()

        packageLoader = PackageLoader(self._client, deviceName)
        packageLoader.setStartDelay(750)
        packageLoader.signals.succeeded.connect(self.packageReloadSucceeded)
        packageLoader.signals.failed.connect(self.packageReloadFailed)
        QThreadPool.globalInstance().start(packageLoader)

        self._dialog = LoadingDialog()
        self._dialog.setText("Fetching packages...")
        self._dialog.exec_()

    def packageReloadSucceeded(self, packageList: List[str], selectedPackage: str):
        self._dialog.close()
        self._capturePane.setPackages(packageList)
        self._capturePane.setSelectedPackage(selectedPackage)

    def packageReloadFailed(
        self,
        errorType: ErrorType,
        deviceName: Optional[str],
        deviceState: Optional[str],
    ):
        self._dialog.close()
        self._capturePane.setPackagesEmpty()

        messageBox = QMessageBox()
        messageBox.setIcon(QMessageBox.Critical)
        messageBox.setWindowTitle("Error")

        if errorType == ErrorType.ConnectionFailure:
            messageBox.setText("Failed to connect to the adb server")
            text = "Have you started the adb server with 'adb server' command?"
            messageBox.setInformativeText(text)
        elif errorType == ErrorType.DeviceNotFound:
            assert deviceName is not None, "deviceName must not be None"
            messageBox.setText(f"Device '{deviceName}' is no longer available")
            text = "Please, reconnect your device to the PC"
            messageBox.setInformativeText(text)
        elif errorType == ErrorType.DeviceStateInvalid:
            assert deviceName is not None, "deviceName must not be None"
            assert deviceState is not None, "deviceState must have a value"
            assert deviceState != "device", "deviceState can't have a 'device' value"
            if deviceState == "unauthorized":
                messageBox.setText(f"Device '{deviceName}' is not authorized")
                text = "Please, allow USB debugging on your device after connecting it to PC"
                messageBox.setInformativeText(text)
            else:
                messageBox.setText(f"Unable to get logs from device '{deviceName}'")
                text = f"Unable to read logs from device which state is '{deviceState}'"
                messageBox.setInformativeText(text)
        else:
            messageBox.setText("Unknown error")
            text = "Please, enable logging to get more info"
            messageBox.setInformativeText(text)

        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec_()

    def packageLoaderSucceeded(self, packageList: List[str], selectedPackage: str):
        self.packageReloadSucceeded(packageList, selectedPackage)
        self._capturePane.exec_()

    def packageLoaderFailed(self, errorType, deviceName, deviceState):
        self.packageReloadFailed(errorType, deviceName, deviceState)
        self._capturePane.exec_()

    def deviceLoaderSucceeded(self, deviceList: List[str], selectedDevice: str):
        self._capturePane.setDevices(deviceList)
        self._capturePane.setSelectedDevice(selectedDevice)
        self._lastSelectedDevice = selectedDevice
        self._dialog.setText("Fetching packages...")

        packageLoader = PackageLoader(
            self._client, selectedDevice, self._lastSelectedPackage
        )
        packageLoader.setStartDelay(500)
        packageLoader.signals.succeeded.connect(self.packageLoaderSucceeded)
        packageLoader.signals.failed.connect(self.packageLoaderFailed)
        QThreadPool.globalInstance().start(packageLoader)

    def deviceLoaderFailed(self, errorType: ErrorType):
        self._dialog.close()
        messageBox = QMessageBox()
        messageBox.setIcon(QMessageBox.Critical)
        messageBox.setWindowTitle("Error")

        if errorType == ErrorType.ConnectionFailure:
            messageBox.setText("Failed to connect to the adb server")
            text = "Have you started the adb server with 'adb server' command?"
            messageBox.setInformativeText(text)
        elif errorType == ErrorType.NoDevicesFound:
            messageBox.setText("No connected devices found")
            text = "Please, connect your device to the PC via USB cable"
            messageBox.setInformativeText(text)
        else:
            messageBox.setText("Unknown error")
            text = "Please, enable logging to get more info"
            messageBox.setInformativeText(text)

        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec_()

    def newCaptureDialog(self):
        deviceLoader = DeviceLoader(self._client, self._lastSelectedDevice)
        deviceLoader.setStartDelay(500)
        deviceLoader.signals.succeeded.connect(self.deviceLoaderSucceeded)
        deviceLoader.signals.failed.connect(self.deviceLoaderFailed)
        QThreadPool.globalInstance().start(deviceLoader)

        self._dialog = LoadingDialog()
        self._dialog.setText("Connecting to ADB server...")
        self._dialog.exec_()
