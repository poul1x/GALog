from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QFileDialog

from galog.app.ui.base.action import BaseAction
from .task import FnReadText, FnReadBinary

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .task import ReadTextFileTask, ReadBinaryFileTask

from enum import Enum


class ReadFileAction(BaseAction):
    def __init__(self, filePath: str):
        super().__init__()
        self._filePath = filePath

    def _succeeded(self):
        self._setSucceeded()

    def _failed(self, msgBrief: str, msgVerbose: str):
        msgBoxErr(msgBrief, msgVerbose)
        self._setFailed()

    def readTextData(self, fnReadText: FnReadText):
        readFileTask = ReadTextFileTask(self._filePath, fnReadText)
        readFileTask.signals.succeeded.connect(self._succeeded)
        readFileTask.signals.failed.connect(self._failed)
        readFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(readFileTask)
        self._loadingDialog.exec_()

    def readBinaryData(self, fnReadBinary: FnReadBinary):
        readFileTask = ReadBinaryFileTask(self._filePath, fnReadBinary)
        readFileTask.signals.succeeded.connect(self._succeeded)
        readFileTask.signals.failed.connect(self._failed)
        readFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(readFileTask)
        self._loadingDialog.exec_()
