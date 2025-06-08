from PyQt5.QtCore import QObject, pyqtSignal

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.errors import DeviceError, InstallError
from galog.app.ui.base.task import Task


class InstallAppTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class InstallAppTask(Task):
    def __init__(self, deviceName: str, apkFilePath: str, adbClient: AdbClient):
        super().__init__()
        self.signals = InstallAppTaskSignals()
        self._deviceName = deviceName
        self._apkFilePath = apkFilePath
        self._adbClient = adbClient

    def entrypoint(self):
        try:
            with deviceRestricted(self._deviceName, self._adbClient) as device:
                device.install(self._apkFilePath)

        except InstallError as e:
            msgBrief = "App installation failed"
            msgVerbose = "Failed to install this APK. Please, ensure the APK is not corrupted and has a valid signature"  # fmt: skip
            self.signals.failed.emit(msgBrief, msgVerbose)

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)

        except Exception:
            self._logger.exception("Got unknown error")
            msgBrief = "Unknown error"
            msgVerbose = "Unknown Error - Possibly a bug in the application"
            self.signals.failed.emit(msgBrief, msgVerbose)

        else:
            self.signals.succeeded.emit()
