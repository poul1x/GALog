from typing import List, Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.controllers.log_messages_pane.log_reader import LogLine


class LogFileWriterSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str, str)


class LogFileWriter(QRunnable):
    _msDelay: Optional[int]

    def __init__(self, filePath: str, logLines: List[LogLine]):
        super().__init__()
        self.signals = LogFileWriterSignals()
        self._filePath = filePath
        self._logLines = logLines
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _logLinesAsText(self):
        result = []
        for line in self._logLines:
            result.append(f"{line.level}/{line.tag}: {line.msg}")

        return "\n".join(result)

    def _writeLogFile(self):
        try:
            with open(self._filePath, "w", encoding="utf-8") as f:
                f.write(self._logLinesAsText())

        except Exception:
            msgBrief = "Failed to save file"
            msgVerbose = "Please, view logs to get more info"
            self.signals.failed.emit(msgBrief, msgVerbose, None)

    def run(self):
        self._delayIfNeeded()
        self._writeLogFile()
        self.signals.succeeded.emit()
