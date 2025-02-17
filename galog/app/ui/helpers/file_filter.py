from enum import Enum
from typing import List


class FileFilter(str, Enum):
    jsonFile = "JSON File (*.json)"
    textFile = "Text File (*.txt)"
    logFile = "Log File (*.log)"
    anyFile = "All Files (*)"


class FileFilterBuilder:

    _items: List[FileFilter]

    def __init__(self) -> None:
        self._items = []

    def add(self, item: FileFilter):
        self._items.append(item)

    def build(self):
        return ";;".join([item.value for item in self._items])

    @staticmethod
    def textFile():
        return FileFilter.textFile.value

    @staticmethod
    def logFile():
        builder = FileFilterBuilder()
        builder.add(FileFilter.logFile)
        builder.add(FileFilter.textFile)
        builder.add(FileFilter.anyFile)
        return builder.build()