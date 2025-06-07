import io
from itertools import count
from typing import IO, Callable, Iterable, List, Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog, QWidget

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.log_reader.log_reader import LogLine
from galog.app.msgbox import msgBoxErr
from ..write_file import WriteFileAction

class WriteLogFileAction(WriteFileAction):
    def _logLineToString(self, line: LogLine):
        return f"{line.level}/{line.tag}: {line.msg}\n"

    def _writeLogFileImpl(self, fd: IO[str], logLines: Iterable[LogLine]):
        for logLine in logLines:
            fd.write(self._logLineToString(logLine))

    def writeLogFile(self, logLines: Iterable[LogLine]):
        self._writeTextData(lambda fd: self._writeLogFileImpl(fd, logLines))
