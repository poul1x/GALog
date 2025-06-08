import re
from typing import IO, Callable, List, Optional

from galog.app.ui.actions.read_file import FileProcessError
from ..read_file import ReadFileAction

from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QFileDialog, QWidget

from queue import Queue

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.log_reader.log_reader import LogLine
from galog.app.msgbox import msgBoxErr

class ReadTagsFileAction(ReadFileAction):

    _result: List[str]

    def __init__(self, filePath: str, parentWidget: Optional[QWidget] = None):
        super().__init__(filePath, parentWidget)
        self._result = []

    def _readLogFileImpl(self, fd: IO[str]):
        self._result = list(filter(lambda s: bool(s), fd.read().split()))

    def readTagsFile(self):
        self._readTextData(self._readLogFileImpl)
        return self._result if self.succeeded() else None