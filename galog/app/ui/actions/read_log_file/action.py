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

REGEX_VTAG = r"^([A-Z])/(.+?): (.*)$"


class LogLineParseError(FileProcessError):
    def __init__(self, lineNum: int) -> None:
        super().__init__(lineNum)

    def lineNum(self):
        return self.args[0]

    def __str__(self) -> str:
        return f"Failed to parse line {self.lineNum()}: not a TAG format"


class SignalsInternal(QObject):
    lineRead = pyqtSignal(LogLine)

class ReadLogFileAction(ReadFileAction):
    def __init__(self, filePath: str, parentWidget: Optional[QWidget] = None):
        super().__init__(filePath, parentWidget)
        self._pattern = re.compile(REGEX_VTAG)
        self._signals = SignalsInternal()

    @property
    def lineRead(self):
        return self._signals.lineRead

    def _lineRead(self, logLine: LogLine):
        self._signals.lineRead.emit(logLine)

    def _parseLogLine(self, lineNum: int, lineText: str):
        match = self._pattern.match(lineText)
        if not match:
            raise LogLineParseError(lineNum)

        return LogLine(
            level=match.group(1),
            tag=match.group(2).rstrip(),
            msg=match.group(3),
            pid=-1,
        )

    def _readLogFileImpl(self, fd: IO[str]):
        for lineNum, lineText in enumerate(fd, start=1):
            lineStripped = lineText.rstrip("\r\n")
            if not lineStripped:
                continue

            self._lineRead(
                self._parseLogLine(lineNum, lineStripped),
            )

            # Prevent flooding UI
            if lineNum % 2000 == 0:
                QThread.msleep(10)

    def readLogFile(self):
        self._readTextData(self._readLogFileImpl)