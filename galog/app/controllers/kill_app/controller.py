import re
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from galog.app.components.dialogs import ErrorDialog, LoadingDialog
from galog.app.device import AdbClient, AdbDevice, deviceRestricted
from galog.app.device.errors import DeviceError
from .app_killer import AppKiller

class KillAppController:
    def __init__(self, adbHost: str, adbPort: int):
        self._client = AdbClient(adbHost, adbPort)

    def appKillerSucceeded(self):
        self._loadingDialog.close()

    def appKillerFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        errorDialog = ErrorDialog()
        errorDialog.setText(msgBrief)
        errorDialog.setInformativeText(msgVerbose)
        errorDialog.exec_()

    def killApp(self, device: str, package: str):
        appKiller = AppKiller(self._client, device, package)
        appKiller.signals.succeeded.connect(self.appKillerSucceeded)
        appKiller.signals.failed.connect(self.appKillerFailed)
        appKiller.setStartDelay(750)
        QThreadPool.globalInstance().start(appKiller)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Killing app...")
        self._loadingDialog.exec_()
