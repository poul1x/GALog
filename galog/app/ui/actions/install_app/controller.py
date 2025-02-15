from typing import Optional
from zipfile import BadZipFile

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog

from galog.app.apk_info import APK
from galog.app.ui.dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.msgbox import msgBoxErr, msgBoxInfo

from .app_installer import AppInstaller


class InstallAppController:
    def __init__(self, client: AdbClient):
        self._client = client
        self._appDebug = False
        self._success = False

    def setAppDebug(self, debug: bool):
        self._appDebug = debug

    def _appInstallerSucceeded(self):
        self._loadingDialog.close()
        # showInfoMsgBox("Success", "App installed successfully")
        self._success = True

    def _appInstallerFailed(
        self, msgBrief: str, msgVerbose: str, details: Optional[str]
    ):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose, details)

    def _dialogCheckingAppExists(self):
        self._loadingDialog.setText("Checking app exists")

    def _dialogInstallingNewApp(self):
        self._loadingDialog.setText("Installing new app")

    def _dialogUninstallingOldApp(self):
        self._loadingDialog.setText("Checking app exists")

    def promptInstallApp(self, device: str):
        openFileDialog = QFileDialog()
        openFileDialog.setFileMode(QFileDialog.ExistingFile)
        openFileDialog.setNameFilter("APK Files (*.apk)")

        if not openFileDialog.exec_():
            return

        selectedFiles = openFileDialog.selectedFiles()
        if not selectedFiles:
            return

        try:
            apkFilePath = selectedFiles[0]
            apk = APK(apkFilePath)

            package = apk.packagename
            if not package:
                raise ValueError("Not a valid APK")

        except (BadZipFile, ValueError):
            msgBrief = "Installation failed"
            msgVerbose = "Provided file is not a valid APK"
            msgBoxErr(msgBrief, msgVerbose)
            return

        appInstaller = AppInstaller(self._client, device, package, apkFilePath)
        appInstaller.signals.succeeded.connect(self._appInstallerSucceeded)
        appInstaller.signals.failed.connect(self._appInstallerFailed)
        appInstaller.signals.checkAppExists.connect(self._dialogCheckingAppExists)
        appInstaller.signals.installingNewApp.connect(self._dialogInstallingNewApp)
        appInstaller.signals.uninstallingOldApp.connect(self._dialogUninstallingOldApp)
        appInstaller.setStageDelay(500)
        QThreadPool.globalInstance().start(appInstaller)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Checking app exists")
        self._loadingDialog.exec_()

    def installApp(self, deviceSerial: str, apkFilePath: str):
        self._success = False
        appInstaller = AppInstaller(self._client, deviceSerial, apkFilePath)
        appInstaller.signals.succeeded.connect(self._appInstallerSucceeded)
        appInstaller.signals.failed.connect(self._appInstallerFailed)
        appInstaller.setStageDelay(500)
        QThreadPool.globalInstance().start(appInstaller)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Installing app...")
        self._loadingDialog.exec_()
        return self._success
