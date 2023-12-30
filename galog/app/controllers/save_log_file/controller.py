from typing import List, Optional
from zipfile import BadZipFile

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from galog.app.apk_info import APK
from galog.app.components.dialogs import LoadingDialog
from galog.app.controllers.log_messages_pane.log_reader import LogLine
from galog.app.device import AdbClient
from galog.app.util.message_box import showErrorMsgBox, showInfoMsgBox

from .log_file_writer import LogFileWriter


class SaveLogFileController:

    def __init__(self, logLines: List[LogLine]) -> None:
        self._logLines = logLines

    def _succeeded(self):
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str, details: Optional[str]):
        self._loadingDialog.close()
        showErrorMsgBox(msgBrief, msgVerbose, details)

    def promptSaveFile(self):
        fileFilter = "LogFiles (*.log);;Log Files (*.txt);;All Files (*)"
        filePath, _ = QFileDialog.getSaveFileName(None, "Save log file", "", fileFilter)

        if not filePath:
            return

        textFileWriter = LogFileWriter(filePath, self._logLines)
        textFileWriter.signals.succeeded.connect(self._succeeded)
        textFileWriter.signals.failed.connect(self._failed)
        textFileWriter.setStartDelay(1000)
        QThreadPool.globalInstance().start(textFileWriter)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Saving file")
        self._loadingDialog.exec_()
