import re
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from loggat.app.components.dialogs import ErrorDialog, LoadingDialog
from loggat.app.device import AdbClient, AdbDevice, deviceRestricted
from loggat.app.device.errors import DeviceError
from .app_runner import AppRunner

class RunAppController:
    def __init__(self, adbHost: str, adbPort: int):
        self._client = AdbClient(adbHost, adbPort)

    def appRunnerSucceeded(self):
        self._loadingDialog.close()

    def appRunnerFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        errorDialog = ErrorDialog()
        errorDialog.setText(msgBrief)
        errorDialog.setInformativeText(msgVerbose)
        errorDialog.exec_()

    def runApp(self, device: str, package: str):
        appRunner = AppRunner(self._client, device, package)
        appRunner.signals.succeeded.connect(self.appRunnerSucceeded)
        appRunner.signals.failed.connect(self.appRunnerFailed)
        appRunner.setStartDelay(750)
        QThreadPool.globalInstance().start(appRunner)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Starting app...")
        self._loadingDialog.exec_()
