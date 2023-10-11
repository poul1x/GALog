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
from .device_loader import DeviceLoader
from .package_loader import PackageLoader

from loggat.app.device import AdbClient, AdbDevice
from loggat.app.device.errors import DeviceError, DeviceNotFound, DeviceStateInvalid, ErrorType

from ...components.capture_pane import CapturePane
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.components.message_view_pane import LogMessageViewPane







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
        self._capturePane.packageNameFromApk.connect(self.packageNameFromApk)
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

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Fetching packages...")
        self._loadingDialog.exec_()

    def packageReloadSucceeded(self, packageList: List[str], selectedPackage: str):
        self._loadingDialog.close()
        self._capturePane.setPackages(packageList)
        self._capturePane.setSelectedPackage(selectedPackage)

    def packageReloadFailed(
        self,
        errorType: ErrorType,
        deviceName: Optional[str],
        deviceState: Optional[str],
    ):
        self._loadingDialog.close()
        self._capturePane.setPackagesEmpty()

        messageBox = ErrorDialog()
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
        self._loadingDialog.setText("Fetching packages...")

        packageLoader = PackageLoader(
            self._client, selectedDevice, self._lastSelectedPackage
        )
        packageLoader.setStartDelay(500)
        packageLoader.signals.succeeded.connect(self.packageLoaderSucceeded)
        packageLoader.signals.failed.connect(self.packageLoaderFailed)
        QThreadPool.globalInstance().start(packageLoader)

    def deviceLoaderFailed(self, errorType: ErrorType):
        self._loadingDialog.close()
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

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Connecting to ADB server...")
        self._loadingDialog.exec_()

    def packageNameFromApk(self):
        openFileDialog = QFileDialog()
        openFileDialog.setFileMode(QFileDialog.ExistingFile)  # Allow selecting an existing file
        openFileDialog.setNameFilter("APK Files (*.apk)")

        if not openFileDialog.exec_():
            return

        selected_files = openFileDialog.selectedFiles()
        if not selected_files:
            return

        apk = APK(selected_files[0])
        packageName = apk.packagename

        if self._capturePane.isPackageInstalled(packageName):
            self._lastSelectedPackage = packageName
            self._capturePane.accept()
        else:
            messageBox = ErrorDialog()
            messageBox.setText(f"Package '{packageName}' is not installed")
            text = "Please, install the package first (ADB -> Install APK)"
            messageBox.setInformativeText(text)
            messageBox.exec_()