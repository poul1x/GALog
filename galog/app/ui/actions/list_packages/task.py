from PyQt5.QtCore import QObject, pyqtSignal

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.errors import DeviceError, DeviceRuntimeError
from galog.app.ui.base.task import Task


class ListPackagesTaskSignals(QObject):
    succeeded = pyqtSignal()
    packageFound = pyqtSignal(str)
    failed = pyqtSignal(DeviceError)


class ListPackagesTask(Task):
    _adbClient: AdbClient

    def __init__(self, deviceName: str, adbClient: AdbClient):
        super().__init__()
        self.signals = ListPackagesTaskSignals()
        self._deviceName = deviceName
        self._adbClient = adbClient

    def entrypoint(self):
        try:
            with deviceRestricted(self._deviceName, self._adbClient) as device:
                for package in device.list_packages():
                    self.signals.packageFound.emit(package)

        except DeviceError as e:
            self.signals.failed.emit(e)

        except Exception:
            self._logger.exception("Got unknown error")
            self.signals.failed.emit(DeviceRuntimeError("Unknown"))

        else:
            self.signals.succeeded.emit()
