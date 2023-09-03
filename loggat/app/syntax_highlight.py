from dataclasses import dataclass
from typing import List
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from enum import IntEnum, auto

from loggat.app.util.painter import takePainter


class SearchItemType(IntEnum):
    url = auto()
    decimalNumber = auto()
    hexadecimalNumber = auto()
    singleQuotedString = auto()
    doubleQuotedString = auto()


@dataclass
class SearchItem:
    type: SearchItemType
    regex: QRegExp


@dataclass
class SearchResult:
    itemType: int
    posBegin: int
    posEnd: int

    # def __init__(self, itemType, posBegin, posEnd) -> None:
    #     super().__init__(None)
    #     self.itemType = itemType
    #     self.posBegin = posBegin
    #     self.posEnd = posEnd



ITEMS = [
    SearchItem(
        type=SearchItemType.url,
        regex=QRegExp(r"\w+://\S+"),
    ),
    SearchItem(
        type=SearchItemType.decimalNumber,
        regex=QRegExp(r"-?\d+(?:\.\d+)?"),
    ),
    SearchItem(
        type=SearchItemType.hexadecimalNumber,
        regex=QRegExp(r"0x[0-9a-zA-Z]+"),
    ),
    SearchItem(
        type=SearchItemType.singleQuotedString,
        regex=QRegExp(r"'[^']*'"),
    ),
    SearchItem(
        type=SearchItemType.doubleQuotedString,
        regex=QRegExp(r'"[^"]*"'),
    ),
]

class SearchItemTaskSignals(QObject):
    finished = pyqtSignal(list)

class SearchItemTask(QRunnable):

    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.signals = SearchItemTaskSignals()

    def run(self):
        result = []
        for item in ITEMS:
            for found in self.search(item):
                result.append(found)

        self.signals.finished.emit(result)


    def search(self, item: SearchItem):
        pos = 0
        while True:
            pos = item.regex.indexIn(self.text, pos)
            if pos == -1:
                break

            begin = pos
            end = begin + item.regex.matchedLength()
            yield SearchResult(item.type, begin, end)
            # yield CustomObject(1)
            # yield 1
            pos = end