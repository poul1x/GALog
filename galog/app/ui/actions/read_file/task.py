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


class ReadFileTaskSignals(QObject):
    succeeded = pyqtSignal()
    failed = pyqtSignal(str, str)


class _ReadFileTask(BaseTask):
    def __init__(self, filePath: str):
        super().__init__()
        self.signals = ReadFileTaskSignals()
        self._filePath = filePath

    @abstractmethod
    def _readFile(self):
        pass

    def _readFileSafe(self):
        try:
            self._readFile()

        except FileNotFoundError as e:
            self._logger.error("Failed to read '%s'. Reason - %s", self._filePath, str(e))  # fmt: skip
            msgBrief = "File not found"
            msgVerbose = "Failed to open file because it was not found"
            self.signals.failed.emit(msgBrief, msgVerbose)

        except PermissionError as e:
            self._logger.error("Failed to read '%s'. Reason - %s", self._filePath, str(e))  # fmt: skip
            msgBrief = "Access Denied"
            msgVerbose = "Unable to read file due to insufficient permissions or file is being used by another process"  # fmt: skip
            self.signals.failed.emit(msgBrief, msgVerbose)

        except UnicodeDecodeError as e:
            self._logger.error("Failed to read '%s'. Reason - %s", self._filePath, str(e))  # fmt: skip
            msgBrief = "Encoding Error"
            msgVerbose = "Failed to decode file content to UTF-8 encoding"
            self.signals.failed.emit(msgBrief, msgVerbose)

        except FileProcessError as e:
            self._logger.error("Failed to read '%s'. Reason - %s", self._filePath, str(e))  # fmt: skip
            self.signals.failed.emit("File Process Error", str(e))

        except Exception:
            self._logger.exception("Failed to read '%s'. Reason - Unknown", self._filePath)  # fmt: skip
            msgBrief = "Unknown Error"
            msgVerbose = "Failed to read file - unknown"
            self.signals.failed.emit(msgBrief, msgVerbose)

    def entrypoint(self):
        self._readFileSafe()
        self.signals.succeeded.emit()


class ReadTextFileTask(_ReadFileTask):
    def __init__(self, filePath: str, fnReadText: FnReadText):
        super().__init__(filePath)
        self._fnReadText = fnReadText

    def _readFile(self):
        self._logger.info("Open '%s', mode='r'", self._filePath)
        with open(self._filePath, "r", encoding="utf-8") as f:
            self._fnReadText(f)


class ReadBinaryFileTask(_ReadFileTask):
    def __init__(self, filePath: str, fnReadBinary: FnReadBinary):
        super().__init__(filePath)
        self._fnReadBinary = fnReadBinary

    def _readFile(self):
        self._logger.info("Open '%s', mode='rb'", self._filePath)
        with open(self._filePath, "rb") as f:
            self._fnReadBinary(f)
