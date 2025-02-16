from PyQt5.QtCore import QThreadPool

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.msgbox import msgBoxErr

from .task import RestartAppTask


class RestartAppAction:
    def __init__(self, client: AdbClient):
        self._client = client

    def appRestartSucceeded(self):
        self._loadingDialog.close()

    def appRestartFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose)

    def restartApp(self, device: str, package: str):
        task = RestartAppTask(self._client, device, package)
        task.signals.succeeded.connect(self.appRestartSucceeded)
        task.signals.failed.connect(self.appRestartFailed)
        task.setStartDelay(750)
        QThreadPool.globalInstance().start(task)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Restarting app...")
        self._loadingDialog.exec_()
