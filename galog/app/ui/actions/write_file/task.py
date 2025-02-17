from abc import abstractmethod
from io import TextIOWrapper
from typing import IO, Callable, List, Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.ui.base.task import BaseTask

from typing import IO, Callable

FnWriteText = Callable[[IO[str]], None]
FnWriteBinary = Callable[[IO[bytes]], None]


class FileProcessError(Exception):
    pass

class ReadFileTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class _WriteFileTask(BaseTask):
    def __init__(self):
        super().__init__()
        self.signals = ReadFileTaskSignals()

    @abstractmethod
    def _writeFile(self):
        pass

    def _writeFileSafe(self):
        try:
            self._writeFile()

        except PermissionError:
            msgBrief = "Access Denied"
            msgVerbose = "Unable to write file due to insufficient permissions or file is being used by another process" # fmt: skip
            self.signals.failed.emit(msgBrief, msgVerbose)

        except Exception:
            msgBrief = "Unknown Error"
            msgVerbose = "Failed to write file - unknown"
            self.signals.failed.emit(msgBrief, msgVerbose)
            raise

    def entrypoint(self):
        self._writeFileSafe()
        self.signals.succeeded.emit()

class WriteTextFileTask(_WriteFileTask):
    def __init__(self, filePath: str, fnWriteText: FnWriteText):
        super().__init__()
        self._filePath = filePath
        self._fnWriteText = fnWriteText

    def _writeFile(self):
        self._logger.info("Open '%s', mode='w'", self._filePath)
        with open(self._filePath, "w", encoding="utf-8") as f:
            self._fnWriteText(f)

class WriteBinaryFileTask(_WriteFileTask):
    def __init__(self, filePath: str, fnWriteBinary: FnWriteBinary):
        super().__init__()
        self._filePath = filePath
        self._fnWriteBinary = fnWriteBinary

    def _writeFile(self):
        self._logger.info("Open '%s', mode='wb'", self._filePath)
        with open(self._filePath, "wb") as f:
            self._fnWriteBinary(f)