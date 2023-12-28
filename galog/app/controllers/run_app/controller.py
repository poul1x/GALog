from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from galog.app.components.dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.util.message_box import showErrorMsgBox

from .app_runner import AppRunner


class RunAppController:
    def __init__(self, adbHost: str, adbPort: int):
        self._client = AdbClient(adbHost, adbPort)
        self._appDebug = False

    def setAppDebug(self, debug: bool):
        self._appDebug = debug

    def _appRunnerSucceeded(self):
        self._loadingDialog.close()

    def _appRunnerFailed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        showErrorMsgBox(msgBrief, msgVerbose)

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
