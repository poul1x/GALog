from dataclasses import dataclass
from time import sleep
from typing import List
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from enum import IntEnum, auto

from re import Pattern


@dataclass
class SearchItem:
    name: str
    pattern: Pattern


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
            for found in self._search(item):
                result.append(found)

        self.signals.finished.emit(result)

    def _search(self, item: SearchItem):
        if item.pattern.groups:
            return self._searchGroups(item)
        else:
            return self._searchPattern(item)

    def _searchPattern(self, item: SearchItem):
        for match in item.pattern.finditer(self.text):
            yield SearchResult(item.name, match.start(), match.end())

    def _searchGroups(self, item: SearchItem):
        for match in item.pattern.finditer(self.text):
            for groupNum in range(1, len(match.groups()) + 1):
                start, end = match.start(groupNum), match.end(groupNum)
                yield SearchResult(item.name, start, end)

