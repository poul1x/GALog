from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QFileDialog

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .task import WriteTextFileTask, WriteBinaryFileTask, FnWriteText, FnWriteBinary

from enum import Enum


class WriteFileAction:
    def __init__(self, filePath: str):
        self.filePath = filePath
        self._initLoadingDialog()

    def _initLoadingDialog(self):
        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Saving file")

    def _succeeded(self):
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose)

    def writeTextData(self, fnReadText: FnWriteText):
        writeFileTask = WriteTextFileTask(self.filePath, fnReadText)
        writeFileTask.signals.succeeded.connect(self._succeeded)
        writeFileTask.signals.failed.connect(self._failed)
        writeFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(writeFileTask)
        self._loadingDialog.exec_()

    def writeBinaryData(self, fnReadBinary: FnWriteBinary):
        writeFileTask = WriteBinaryFileTask(self.filePath, fnReadBinary)
        writeFileTask.signals.succeeded.connect(self._succeeded)
        writeFileTask.signals.failed.connect(self._failed)
        writeFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(writeFileTask)
        self._loadingDialog.exec_()
