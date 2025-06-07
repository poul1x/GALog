import io
from itertools import count
from typing import IO, Callable, Iterable, List, Optional

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog, QWidget

from galog.app.ui.quick_dialogs import LoadingDialog
from galog.app.log_reader.log_reader import LogLine
from galog.app.msgbox import msgBoxErr
from ..write_file import WriteFileAction

class WriteTagsFileAction(WriteFileAction):
    def _writeTagsFileImpl(self, f: IO[str], tags: Iterable[str]):
        f.write("\n".join(tags))

    def writeTagsFile(self, tags: Iterable[str]):
        self._writeTextData(lambda fd: self._writeTagsFileImpl(fd, tags))
