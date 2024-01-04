from typing import Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.device import AdbClient, AdbDevice, deviceRestricted
from galog.app.device.errors import DeviceError, InstallError


class AppInstallerSignals(QObject):
    checkAppExists = pyqtSignal()
    uninstallingOldApp = pyqtSignal()
    installingNewApp = pyqtSignal()
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str, str)


class AppInstaller(QRunnable):
    _client: AdbClient
    _msDelay: Optional[int]

    def __init__(
        self, client: AdbClient, deviceName: str, packageName: str, apkFilePath: str
    ):
        super().__init__()
        self.signals = AppInstallerSignals()
        self._deviceName = deviceName
        self._packageName = packageName
        self._apkFilePath = apkFilePath
        self._client = client
        self._msDelay = None

    def setStageDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _appExists(self, device: AdbDevice):
        self.signals.checkAppExists.emit()
        self._delayIfNeeded()
        return device.is_installed(self._packageName)

    def _installApp(self, device: AdbDevice):
        self.signals.installingNewApp.emit()
        self._delayIfNeeded()
        device.install(self._apkFilePath)

    def _uninstallApp(self, device: AdbDevice):
        self.signals.uninstallingOldApp.emit()
        self._delayIfNeeded()
        device.uninstall(self._packageName)

    def _execInstallApp(self):
        with deviceRestricted(self._client, self._deviceName) as device:
            if self._appExists(device):
                self._uninstallApp(device)
            self._installApp(device)

    def run(self):
        try:
            self._delayIfNeeded()
            self._execInstallApp()
            self.signals.succeeded.emit()

        except InstallError as e:
            msgBrief = "Operation failed"
            msgVerbose = "Error occurred during app installation (see details)"
            self.signals.failed.emit(msgBrief, msgVerbose, str(e))

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose, None)
