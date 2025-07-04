from PyQt5.QtCore import QObject, pyqtSignal

from galog.app.device import AdbClient, DeviceInfo, deviceListWithInfo
from galog.app.device.errors import DeviceError
from galog.app.ui.base.task import Task


class ListDevicesTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)
    deviceFound = pyqtSignal(DeviceInfo)


class ListDevicesTask(Task):
    _adbClient: AdbClient

    def __init__(self, adbClient: AdbClient):
        super().__init__()
        self.signals = ListDevicesTaskSignals()
        self._adbClient = adbClient

    def entrypoint(self):
        try:
            for device in deviceListWithInfo(self._adbClient):
                self.signals.deviceFound.emit(device)

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
        except Exception:
            self._logger.exception("Got unknown error")
            msgBrief = "Unknown error"
            msgVerbose = "Unknown Error - Possibly a bug in the application"
            self.signals.failed.emit(msgBrief, msgVerbose)
        else:
            self.signals.succeeded.emit()
