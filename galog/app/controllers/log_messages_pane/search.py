from dataclasses import dataclass
from time import sleep
from typing import List, Optional
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from enum import IntEnum, auto

from re import Pattern


@dataclass
class SearchItem:
    name: str
    pattern: Pattern
    priority: int
    groups: Optional[List[int]]


@dataclass
class SearchResult:
    name: int
    priority: int
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

        def key(item: SearchItem):
            return item.priority

        self.signals.finished.emit(sorted(result, key=key))

    def _search(self, item: SearchItem):
        if item.groups is None or item.pattern.groups == 0:
            return self._searchPattern(item)
        else:
            return self._searchGroups(item)

    def _searchPattern(self, item: SearchItem):
        for match in item.pattern.finditer(self.text):
            yield SearchResult(item.name, item.priority, match.start(), match.end())

    def _searchGroups(self, item: SearchItem):
        for match in item.pattern.finditer(self.text):
            for groupNum in range(1, len(match.groups()) + 1):
                if item.groups and groupNum not in item.groups:
                    continue

                start, end = match.start(groupNum), match.end(groupNum)
                yield SearchResult(item.name, item.priority, start, end)
