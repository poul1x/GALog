from typing import List, Optional

from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtWidgets import QFileDialog
from .task import FnReadText, FnReadBinary

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.msgbox import msgBoxErr

from .task import ReadTextFileTask, ReadBinaryFileTask

from enum import Enum


class ReadFileAction:
    def __init__(self, filePath: str):
        self.filePath = filePath
        self._initLoadingDialog()

    def _initLoadingDialog(self):
        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText("Reading file")

    def _succeeded(self):
        self._loadingDialog.close()

    def _failed(self, msgBrief: str, msgVerbose: str):
        self._loadingDialog.close()
        msgBoxErr(msgBrief, msgVerbose)

    def setDialogText(self, text: str):
        self._loadingDialog.setText(text)

    def readTextData(self, fnReadText: FnReadText):
        readFileTask = ReadTextFileTask(self.filePath, fnReadText)
        readFileTask.signals.succeeded.connect(self._succeeded)
        readFileTask.signals.failed.connect(self._failed)
        readFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(readFileTask)
        self._loadingDialog.exec_()

    def readBinaryData(self, fnReadBinary: FnReadBinary):
        readFileTask = ReadBinaryFileTask(self.filePath, fnReadBinary)
        readFileTask.signals.succeeded.connect(self._succeeded)
        readFileTask.signals.failed.connect(self._failed)
        readFileTask.setStartDelay(700)

        QThreadPool.globalInstance().start(readFileTask)
        self._loadingDialog.exec_()
