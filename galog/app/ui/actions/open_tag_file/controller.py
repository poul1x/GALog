from typing import List, Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog

from galog.app.ui.dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .tag_file_reader import TagFileReader


class OpenTagFileController:
    _result: List[str]

    def __init__(self) -> None:
        self._result = []

    def _succeeded(self, result: list):
        self._result = result
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str, details: Optional[str]):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose, details)

    def promptOpenFile(self):
        fileFilter = "Text File (*.txt);;All Files (*)"
        filePath, _ = QFileDialog.getOpenFileName(None, "Open File As", "", fileFilter)

        if not filePath:
            return

        textFileWriter = TagFileReader(filePath)
        textFileWriter.signals.succeeded.connect(self._succeeded)
        textFileWriter.signals.failed.connect(self._failed)
        textFileWriter.setStartDelay(1000)
        QThreadPool.globalInstance().start(textFileWriter)

        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Reading file")
        self._loadingDialog.exec_()
        return self._result
