from PyQt5.QtCore import QThreadPool

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.msgbox import msgBoxErr

from .app_runner import AppRunner


class RunAppController:
    def __init__(self):
        self._client = AdbClient()
        self._appDebug = False

    def setAppDebug(self, debug: bool):
        self._appDebug = debug

    def _appRunnerSucceeded(self):
        self._loadingDialog.close()

    def _appRunnerFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose)

    def runApp(self, device: str, package: str):
        appRunner = AppRunner(self._client, device, package)
        appRunner.signals.succeeded.connect(self._appRunnerSucceeded)
        appRunner.signals.failed.connect(self._appRunnerFailed)
        appRunner.setAppDebug(self._appDebug)
        appRunner.setStartDelay(750)
        QThreadPool.globalInstance().start(appRunner)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(f"Starting app...")
        self._loadingDialog.exec_()
