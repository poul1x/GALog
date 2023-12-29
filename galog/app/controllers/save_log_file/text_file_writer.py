from typing import Optional

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TextFileWriterSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str, str)


class TextFileWriter(QRunnable):
    _msDelay: Optional[int]

    def __init__(self, filePath: str, content: str):
        super().__init__()
        self.signals = TextFileWriterSignals()
        self._filePath = filePath
        self._content = content
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _writeTextFile(self):
        try:
            with open(self._filePath, "w") as f:
                f.write(self._content)

        except Exception:
            msgBrief = "Failed to save file"
            msgVerbose = "Please, view logs to get more info"
            self.signals.failed.emit(msgBrief, msgVerbose)

    def run(self):
        self._delayIfNeeded()
        self._writeTextFile()
        self.signals.succeeded.emit()
