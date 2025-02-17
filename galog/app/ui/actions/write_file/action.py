from typing import List, Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .task import WriteFileTask


class WriteFileAction:
    def __init__(self, tags: List[str]) -> None:
        self._tags = tags

    def _succeeded(self):
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str, details: Optional[str]):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose, details)

    def askFilePath(self):
        fileFilter = "Text File (*.txt);;All Files (*)"
        filePath, _ = QFileDialog.getSaveFileName(None, "Save tags", "", fileFilter)

        if not filePath:
            return

        textFileWriter = WriteFileTask(filePath, self._tags)
        textFileWriter.signals.succeeded.connect(self._succeeded)
        textFileWriter.signals.failed.connect(self._failed)
        textFileWriter.setStartDelay(1000)
        QThreadPool.globalInstance().start(textFileWriter)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Saving file")
        self._loadingDialog.exec_()
