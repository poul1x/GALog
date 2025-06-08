from enum import Enum
import os
from typing import List, Optional

from PyQt5.QtWidgets import QFileDialog


class FileExtensionFilter(str, Enum):
    jsonFile = "JSON File (*.json)"
    TextFile = "Text File (*.txt)"
    LogFile = "Log File (*.log)"
    AnyFile = "All Files (*)"


class FileExtensionFilterBuilder:
    _items: List[FileExtensionFilter]

    def __init__(self) -> None:
        self._items = []

    def add(self, item: FileExtensionFilter):
        self._items.append(item)

    def build(self):
        return ";;".join([item.value for item in self._items])

    @staticmethod
    def textFile():
        return FileExtensionFilter.TextFile.value

    @staticmethod
    def logFile():
        builder = FileExtensionFilterBuilder()
        builder.add(FileExtensionFilter.LogFile)
        builder.add(FileExtensionFilter.TextFile)
        builder.add(FileExtensionFilter.AnyFile)
        return builder.build()


class FilePicker:
    def __init__(
        self,
        caption: str = "Select File(s)",
        directory: Optional[str] = None,
        extensionFilter: FileExtensionFilter = FileExtensionFilter.AnyFile,
    ):
        self._caption = caption
        self._directory = directory
        self._extensionFilter = extensionFilter
        self._lastSelectedDir = None

    def _saveSelectedPath(self, filePath: str):
        if not filePath:
            return

        self._lastSelectedDir = os.path.dirname(filePath)

    def _getOpenFileName(self):
        return QFileDialog.getOpenFileName(
            directory=self._directory,
            filter=self._extensionFilter,
            caption=self._caption,
        )[0]

    def _getSaveFileName(self):
        return QFileDialog.getSaveFileName(
            directory=self._directory,
            filter=self._extensionFilter,
            caption=self._caption,
        )[0]

    def askOpenFileRead(self):
        filePath = self._getOpenFileName()
        self._saveSelectedPath(filePath)
        return filePath

    def askOpenFileWrite(self):
        filePath = self._getSaveFileName()
        self._saveSelectedPath(filePath)
        return filePath

    def selectedDirectory(self):
        return self._lastSelectedDir

    def hasSelectedDirectory(self):
        return self._lastSelectedDir is not None