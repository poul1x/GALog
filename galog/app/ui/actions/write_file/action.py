from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget
from galog.app.ui.base.action import Action

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .task import WriteTextFileTask, WriteBinaryFileTask, FnWriteText, FnWriteBinary

from enum import Enum


class WriteFileAction(Action):
    def __init__(self, filePath: str, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self._filePath = filePath

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def writeTextData(self, fnReadText: FnWriteText):
        writeFileTask = WriteTextFileTask(self._filePath, fnReadText)
        writeFileTask.signals.succeeded.connect(self._succeeded)
        writeFileTask.signals.failed.connect(self._failed)
        writeFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(writeFileTask)
        self._execLoadingDialog()

    def writeBinaryData(self, fnReadBinary: FnWriteBinary):
        writeFileTask = WriteBinaryFileTask(self._filePath, fnReadBinary)
        writeFileTask.signals.succeeded.connect(self._succeeded)
        writeFileTask.signals.failed.connect(self._failed)
        writeFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(writeFileTask)
        self._execLoadingDialog()
