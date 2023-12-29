from typing import Optional
from zipfile import BadZipFile

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from galog.app.apk_info import APK
from galog.app.components.dialogs import LoadingDialog
from galog.app.device import AdbClient
from galog.app.util.message_box import showErrorMsgBox, showInfoMsgBox

from .text_file_writer import TextFileWriter


class SaveLogFileController:

    def __init__(self, content: str) -> None:
        self._content = content

    def _succeeded(self):
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str, details: Optional[str]):
        self._loadingDialog.close()
        showErrorMsgBox(msgBrief, msgVerbose, details)

    def promptSaveFile(self):
        fileFilter = "LogFiles (*.log);;Text Files (*.txt);;All Files (*)"
        filePath, _ = QFileDialog.getSaveFileName(None, "Save File As", "", fileFilter)

        if not filePath:
            return

        textFileWriter = TextFileWriter(filePath, self._content)
        textFileWriter.signals.succeeded.connect(self._succeeded)
        textFileWriter.signals.failed.connect(self._failed)
        textFileWriter.setStartDelay(1000)
        QThreadPool.globalInstance().start(textFileWriter)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Saving file")
        self._loadingDialog.exec_()
