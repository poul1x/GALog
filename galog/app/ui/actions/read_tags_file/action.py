from typing import IO, List, Optional

from PyQt5.QtWidgets import QWidget

from ..read_file import ReadFileAction


class ReadTagsFileAction(ReadFileAction):
    _result: List[str]

    def __init__(self, filePath: str, parentWidget: Optional[QWidget] = None):
        super().__init__(filePath, parentWidget)
        self._result = []

    def _readLogFileImpl(self, fd: IO[str]):
        self._result = list(filter(lambda s: bool(s), fd.read().split()))

    def readTagsFile(self):
        self._readTextData(self._readLogFileImpl)
        return self._result if self.succeeded() else None
