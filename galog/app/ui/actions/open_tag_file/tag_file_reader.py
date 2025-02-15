from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal


class TagFileReaderSignals(QObject):
    succeeded = pyqtSignal(list)
    failed = pyqtSignal(str, str, str)


class TagFileReader(QRunnable):
    def __init__(self, filePath: str):
        super().__init__()
        self.signals = TagFileReaderSignals()
        self._filePath = filePath
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _readContentFromFile(self):
        try:
            result = []
            with open(self._filePath, "r") as f:
                result = list(filter(lambda x: bool(x), f.read().split()))

        except Exception:
            msgBrief = "Failed to open file - unknown"
            msgVerbose = "Please, view logs to get more info"
            self.signals.failed.emit(msgBrief, msgVerbose, None)

        return result

    def run(self):
        self._delayIfNeeded()
        tags = self._readContentFromFile()
        self.signals.succeeded.emit(tags)
