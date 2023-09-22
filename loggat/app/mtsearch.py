from dataclasses import dataclass
from time import sleep
from typing import List
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from enum import IntEnum, auto

# class SearchItemType(IntEnum):
#     url = auto()
#     decimalNumber = auto()
#     hexadecimalNumber = auto()
#     singleQuotedString = auto()
#     doubleQuotedString = auto()


@dataclass
class SearchItem:
    name: str
    pattern: QRegExp

@dataclass
class SearchResult:
    name: int
    begin: int
    end: int

class SearchItemTaskSignals(QObject):
    finished = pyqtSignal(list)

class SearchItemTask(QRunnable):

    def __init__(self, text: str, searchItems: List[SearchItem]):
        super().__init__()
        self.signals = SearchItemTaskSignals()
        self.searchItems = searchItems
        self.text = text

    def run(self):
        result = []
        for item in self.searchItems:
            for found in self.search(item):
                result.append(found)

        self.signals.finished.emit(result)


    def search(self, item: SearchItem):
        pos = 0
        while True:
            pos = item.pattern.indexIn(self.text, pos)
            if pos == -1:
                break

            begin = pos
            end = begin + item.pattern.matchedLength()
            yield SearchResult(item.name, begin, end)
            pos = end