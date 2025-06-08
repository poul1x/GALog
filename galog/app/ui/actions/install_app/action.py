from typing import Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget

from galog.app.device import AdbClient
from galog.app.ui.base.action import Action

from .task import InstallAppTask


class InstallAppAction(Action):
    def __init__(self, adbClient: AdbClient, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self.setLoadingDialogText("Installing App")
        self._adbClient = adbClient

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def installApp(self, deviceSerial: str, apkFilePath: str):
        appInstaller = InstallAppTask(deviceSerial, apkFilePath, self._adbClient)
        appInstaller.signals.succeeded.connect(self._succeeded)
        appInstaller.signals.failed.connect(self._failed)
        appInstaller.setStartDelay(500)

        QThreadPool.globalInstance().start(appInstaller)
        self._execLoadingDialog()
        return self.succeeded()
