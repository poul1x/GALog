import re

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.log_reader.log_reader import LogLine

REGEX_VTAG = r"^([A-Z])/(.+?): (.*)$"


class LogFileReaderSignals(QObject):
    succeeded = pyqtSignal(list)
    failed = pyqtSignal(str, str, str)


class LogFileReader(QRunnable):
    def __init__(self, filePath: str):
        super().__init__()
        self.signals = LogFileReaderSignals()
        self._pattern = re.compile(REGEX_VTAG)
        self._filePath = filePath
        self._msDelay = None

    def setStartDelay(self, ms: int):
        self._msDelay = ms

    def _delayIfNeeded(self):
        if self._msDelay:
            QThread.msleep(self._msDelay)

    def _parseLogLine(self, line: str):
        match = self._pattern.match(line)
        if not match:
            raise ValueError("Failed to parse log line")

        return LogLine(
            level=match.group(1),
            tag=match.group(2).rstrip(),
            msg=match.group(3),
            pid=-1,
        )

    def _readLogFile(self):
        try:
            result = []
            with open(self._filePath, "r", encoding="utf-8") as f:
                for rawLogLine in f:
                    strippedLine = rawLogLine.rstrip("\r\n")
                    if not strippedLine:
                        continue
                    line = self._parseLogLine(strippedLine)
                    result.append(line)

        except ValueError:
            msgBrief = "Failed to parse file: line %d" % len(result)
            msgVerbose = "Please, ensure the file contains log output in 'tag' format"
            self.signals.failed.emit(msgBrief, msgVerbose, None)

        except Exception:
            msgBrief = "Failed to open file - unknown"
            msgVerbose = "Please, view logs to get more info"
            self.signals.failed.emit(msgBrief, msgVerbose, None)

        return result

    def run(self):
        self._delayIfNeeded()
        lines = self._readLogFile()
        self.signals.succeeded.emit(lines)
