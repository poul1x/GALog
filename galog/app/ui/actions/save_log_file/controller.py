from typing import List, Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog

from galog.app.ui.dialogs import LoadingDialog
from galog.app.log_reader.log_reader import LogLine
from galog.app.msgbox import msgBoxErr

from .log_file_writer import LogFileWriter


class SaveLogFileController:
    def __init__(self, logLines: List[LogLine]) -> None:
        self._logLines = logLines

    def _succeeded(self):
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str, details: Optional[str]):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose, details)

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
