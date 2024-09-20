from PySide6.QtCore import QThreadPool

from galog.app.components.dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.util.message_box import showErrorMsgBox

from .app_killer import AppKiller


class KillAppController:
    def __init__(self):
        self._client = AdbClient()

    def appKillerSucceeded(self):
        self._loadingDialog.close()

    def appKillerFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        showErrorMsgBox(msgBrief, msgVerbose)

    def killApp(self, device: str, package: str):
        appKiller = AppKiller(self._client, device, package)
        appKiller.signals.succeeded.connect(self.appKillerSucceeded)
        appKiller.signals.failed.connect(self.appKillerFailed)
        appKiller.setStartDelay(750)
        QThreadPool.globalInstance().start(appKiller)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Killing app...")
        self._loadingDialog.exec()
