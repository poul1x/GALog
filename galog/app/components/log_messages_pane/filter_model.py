from typing import Callable, List
from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel, Qt

from .data_model import Columns


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._regExpFilterEnabled = False
        self._tagFilterEnabled = False
        self._tagFilterFn = None

    def filteringEnabled(self):
        return self._regExpFilterEnabled

    def setFilteringEnabled(self, enabled: bool):
        self._regExpFilterEnabled = enabled
        self.invalidateFilter()

    def tagFilteringEnabled(self):
        return self._tagFilterEnabled

    def setTagFilteringEnabled(self, enabled: bool):
        self._tagFilterEnabled = enabled
        self.invalidateFilter()

    def setTagFilteringFn(self, fn: Callable[[str], bool]):
        self._tagFilterFn = fn
        self.setTagFilteringEnabled(True)

    def clearTagFilteringItems(self):
        self._tagFilterFn = None
        self.setTagFilteringEnabled(False)

    def filterByRegExp(self, sourceRow: int, sourceParent: QModelIndex):
        if not self._regExpFilterEnabled:
            return True

        filterRegExp = self.filterRegExp()
        if filterRegExp.isEmpty():
            return True

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, Columns.logMessage, sourceParent)
        return filterRegExp.indexIn(sourceModel.data(indexBody)) != -1

    def filterByTag(self, sourceRow: int, sourceParent: QModelIndex):
        if not self._tagFilterEnabled:
            return True

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, Columns.tagName, sourceParent)

        assert self._tagFilterFn is not None
        return self._tagFilterFn(sourceModel.data(indexBody))

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        return (
            True
            and self.filterByTag(sourceRow, sourceParent)
            and self.filterByRegExp(sourceRow, sourceParent)
        )
