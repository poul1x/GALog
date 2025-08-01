from abc import abstractmethod
from typing import IO, Callable

from PyQt5.QtCore import QObject, pyqtSignal

from galog.app.ui.base.task import Task

FnWriteText = Callable[[IO[str]], None]
FnWriteBinary = Callable[[IO[bytes]], None]


class FileProcessError(Exception):
    pass


class ReadFileTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class _WriteFileTask(Task):
    def __init__(self, filePath: str):
        super().__init__()
        self.signals = ReadFileTaskSignals()
        self._filePath = filePath

    @abstractmethod
    def _writeFile(self):
        pass

    def _writeFileSafe(self):
        try:
            self._writeFile()

        except PermissionError as e:
            self._logger.error("Failed to write '%s'. Reason - %s", self._filePath, str(e))  # fmt: skip
            msgBrief = "Access Denied"
            msgVerbose = "Unable to write file due to insufficient permissions or file is being used by another process"  # fmt: skip
            self.signals.failed.emit(msgBrief, msgVerbose)

        except Exception:
            self._logger.error("Failed to write '%s'. Reason - Unknown", self._filePath)  # fmt: skip
            msgBrief = "Unknown Error"
            msgVerbose = "Failed to write file - unknown"
            self.signals.failed.emit(msgBrief, msgVerbose)

    def entrypoint(self):
        self._writeFileSafe()
        self.signals.succeeded.emit()


class WriteTextFileTask(_WriteFileTask):
    def __init__(self, filePath: str, fnWriteText: FnWriteText):
        super().__init__(filePath)
        self._fnWriteText = fnWriteText

    def _writeFile(self):
        self._logger.info("Open '%s', mode='w'", self._filePath)
        with open(self._filePath, "w", encoding="utf-8") as f:
            self._fnWriteText(f)


class WriteBinaryFileTask(_WriteFileTask):
    def __init__(self, filePath: str, fnWriteBinary: FnWriteBinary):
        super().__init__(filePath)
        self._fnWriteBinary = fnWriteBinary

    def _writeFile(self):
        self._logger.info("Open '%s', mode='wb'", self._filePath)
        with open(self._filePath, "wb") as f:
            self._fnWriteBinary(f)
