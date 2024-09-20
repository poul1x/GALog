from dataclasses import dataclass
from re import Pattern
from typing import List, Set

from PySide6.QtCore import QObject, QRunnable, Signal


@dataclass
class SearchItem:
    name: str
    pattern: Pattern
    priority: int
    groups: Set[int]


@dataclass
class SearchResult:
    name: str
    priority: int
    groupNum: int
    begin: int
    end: int


class SearchItemTaskSignals(QObject):
    finished = Signal(list)


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

        def key(item: SearchResult):
            return item.priority

        self.signals.finished.emit(sorted(result, key=key))

    def _search(self, item: SearchItem):
        #
        # We need to find all matches (if needed), including group matches (if needed),
        # and convert them to SearchResult structures, giving lower priority
        # for whole matches and higher priority for group matches
        #
        # groupNum = 0 stands for whole match
        # groupNum > 0 stands for group matches
        #

        for match in item.pattern.finditer(self.text):
            for groupNum in range(0, len(match.groups()) + 1):
                if groupNum not in item.groups:
                    continue

                start, end = match.span(groupNum)
                if start == -1 or end == -1:
                    continue

                yield SearchResult(
                    item.name,
                    item.priority + groupNum,
                    groupNum,
                    start,
                    end,
                )
