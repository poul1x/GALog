from typing import List, Optional

from PySide6.QtCore import QObject, QRunnable, QThread, Signal


class TagFileWriterSignals(QObject):
    succeeded = Signal()
    failed = Signal(str, str, str)


class TagFileWriter(QRunnable):
    _msDelay: Optional[int]

    def __init__(self, filePath: str, tags: List[str]):
        super().__init__()
        self.signals = TagFileWriterSignals()
        self._filePath = filePath
        self._tags = tags
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _writeContentToFile(self):
        try:
            with open(self._filePath, "w") as f:
                f.write("\n".join(self._tags))

        except Exception:
            msgBrief = "Failed to save file"
            msgVerbose = "Please, view logs to get more info"
            self.signals.failed.emit(msgBrief, msgVerbose, None)

    def run(self):
        self._delayIfNeeded()
        self._writeContentToFile()
        self.signals.succeeded.emit()
