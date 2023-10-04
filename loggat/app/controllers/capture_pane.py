from datetime import datetime
import os
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yaml
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

from ppadb.client import Client
from ppadb.device import Device


class CapturePaneController:
    capturePane: Optional[CapturePane]

    def __init__(self, adb_host: str, adb_port: int) -> None:
        self.setAdbAddr(adb_host, adb_port)
        self.selectedDevice = None
        self.selectedPackage = None
        self.capturePane = None

    def getSelectedDevice(self):
        assert self.selectedDevice is not None
        return self.selectedDevice

    def getSelectedPackage(self):
        assert self.selectedPackage is not None
        return self.selectedPackage

    def captureTargetSelected(self):
        return self.selectedPackage is not None and self.selectedDevice is not None

    def setAdbAddr(self, adb_host: str, adb_port: int) -> None:
        self.client = Client(adb_host, adb_port)

    def setWidget(self, capturePane: CapturePane) -> None:
        self.capturePane = capturePane
        self.capturePane.deviceChanged.connect(self.deviceChanged)
        self.capturePane.packageSelected.connect(self.packageSelected)

    def packageSelected(self, packageName: str):
        self.selectedPackage = packageName

    def deviceChanged(self, deviceName: str):
        self.selectedDevice = deviceName

        try:
            device: Device = self.client.device(deviceName)
            if not device:
                raise Exception("Device not found")
        except Exception as e:
            # ADB connection error
            msg = f"Failed to get device '{deviceName}'. Reason - {str(e)}"
            QMessageBox.critical(self.capturePane, "Error", msg)
            self.capturePane.setPackagesEmpty()
            return

        try:
            packages = device.list_packages()
            self.capturePane.setPackages(packages)
        except Exception as e:
            name = device.serial
            msg = f"Failed to get packages for device {name}. Reason - {str(e)}"
            QMessageBox.critical(self.capturePane, "Error", msg)
            self.capturePane.setPackagesEmpty()

    def newCaptureDialog(self):
        try:
            devices: List[Device] = self.client.devices()
        except Exception as e:
            msg = f"Failed to get devices. Reason - {str(e)}"
            QMessageBox.critical(self.capturePane, "Error", msg)
            self.capturePane.close()
            return

        if len(devices) == 0:
            msg = f"No devices connected to adb"
            QMessageBox.critical(self.capturePane, "Error", msg)
            self.capturePane.close()
            return

        packages = []
        deviceNames = [dev.serial for dev in devices]

        try:
            i = deviceNames.index(self.selectedDevice)
        except ValueError:
            i = 0

        self.selectedDevice = devices[i].serial

        try:
            packages = devices[i].list_packages()
            self.capturePane.setPackages(packages)
        except Exception as e:
            name = devices[i].serial
            msg = f"Failed to packages for device {name}. Reason - {str(e)}"
            QMessageBox.critical(self.capturePane, "Error", msg)
            self.capturePane.setPackagesEmpty()

        self.capturePane.setDevices(deviceNames)
        self.capturePane.setSelectedDevice(deviceNames[i])
        self.capturePane.exec_()
