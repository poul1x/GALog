from abc import abstractmethod
from enum import Enum, auto
from io import TextIOWrapper
from typing import IO, Callable, List, Optional

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal

from galog.app.ui.base.task import BaseTask

from typing import IO, Callable

FnReadText = Callable[[IO[str]], None]
FnReadBinary = Callable[[IO[bytes]], None]

class FileProcessError(Exception):
    pass

class ErrorCode(int, Enum):
    unknownError = 0
    permissionError = auto()
    fileNotFound = auto()
    contentDecodeError = auto()
    contentProcessError = auto()


class ReadFileTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class _ReadFileTask(BaseTask):
    def __init__(self):
        super().__init__()
        self.signals = ReadFileTaskSignals()

    @abstractmethod
    def _readFile(self):
        pass

    def _readFileSafe(self):
        try:
            self._readFile()

        except FileNotFoundError:
            msgBrief = "File not found"
            msgVerbose = "Failed to open file because it was not found"
            self.signals.failed.emit(msgBrief, msgVerbose)

        except PermissionError:
            msgBrief = "Access Denied"
            msgVerbose = "Unable to read file due to insufficient permissions or file is being used by another process" # fmt: skip
            self.signals.failed.emit(msgBrief, msgVerbose)

        except UnicodeDecodeError:
            msgBrief = "Encoding Error"
            msgVerbose = "Failed to decode file content to UTF-8 encoding"
            self.signals.failed.emit(msgBrief, msgVerbose)

        except FileProcessError as e:
            msgBrief = "File Process Error"
            self.signals.failed.emit(msgBrief, str(e))

        except Exception:
            msgBrief = "Unknown Error"
            msgVerbose = "Failed to read file - unknown"
            self.signals.failed.emit(msgBrief, msgVerbose)
            raise

    def entrypoint(self):
        self._readFileSafe()
        self.signals.succeeded.emit()

class ReadTextFileTask(_ReadFileTask):
    def __init__(self, filePath: str, fnReadText: FnReadText):
        super().__init__()
        self._filePath = filePath
        self._fnReadText = fnReadText

    def _readFile(self):
        self._logger.info("Open '%s', mode='r'", self._filePath)
        with open(self._filePath, "r", encoding="utf-8") as f:
            self._fnReadText(f)

class ReadBinaryFileTask(_ReadFileTask):
    def __init__(self, filePath: str, fnReadBinary: FnReadBinary):
        super().__init__()
        self._filePath = filePath
        self._fnReadBinary = fnReadBinary

    def _readFile(self):
        self._logger.info("Open '%s', mode='rb'", self._filePath)
        with open(self._filePath, "rb") as f: # TODO: open may fail -> use failed signal
            self._fnReadBinary(f)