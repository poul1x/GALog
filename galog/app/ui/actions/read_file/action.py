from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QWidget

from galog.app.ui.base.action import BaseAction
from .task import FnReadText, FnReadBinary

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .task import ReadTextFileTask, ReadBinaryFileTask

from enum import Enum


class ReadFileAction(BaseAction):
    def __init__(self, filePath: str, parentWidget: Optional[QWidget] = None):
        super().__init__(parentWidget)
        self._filePath = filePath

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def readTextData(self, fnReadText: FnReadText):
        readFileTask = ReadTextFileTask(self._filePath, fnReadText)
        readFileTask.signals.succeeded.connect(self._succeeded)
        readFileTask.signals.failed.connect(self._failed)
        readFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(readFileTask)
        self._execLoadingDialog()

    def readBinaryData(self, fnReadBinary: FnReadBinary):
        readFileTask = ReadBinaryFileTask(self._filePath, fnReadBinary)
        readFileTask.signals.succeeded.connect(self._succeeded)
        readFileTask.signals.failed.connect(self._failed)
        readFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(readFileTask)
        self._execLoadingDialog()
