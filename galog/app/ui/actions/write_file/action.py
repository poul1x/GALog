from typing import Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget

from galog.app.ui.base.action import Action

from .task import FnWriteBinary, FnWriteText, WriteBinaryFileTask, WriteTextFileTask


class WriteFileAction(Action):
    def __init__(self, filePath: str, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self._filePath = filePath

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def _writeTextData(self, fnReadText: FnWriteText):
        writeFileTask = WriteTextFileTask(self._filePath, fnReadText)
        writeFileTask.signals.succeeded.connect(self._succeeded)
        writeFileTask.signals.failed.connect(self._failed)
        writeFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(writeFileTask)
        self._execLoadingDialog()

    def _writeBinaryData(self, fnReadBinary: FnWriteBinary):
        writeFileTask = WriteBinaryFileTask(self._filePath, fnReadBinary)
        writeFileTask.signals.succeeded.connect(self._succeeded)
        writeFileTask.signals.failed.connect(self._failed)
        writeFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(writeFileTask)
        self._execLoadingDialog()
