from typing import Callable

from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel, Qt


class RegExpFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(0)
        self._enabled = False

    def filteringEnabled(self):
        return self._enabled

    def setFilteringEnabled(self, enabled: bool):
        self._enabled = enabled
        self.invalidateFilter()

    def filteringColumn(self):
        return self.filterKeyColumn()

    def setFilteringColumn(self, column: int):
        self.setFilterKeyColumn(column)
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        if not self._enabled:
            return True

        filterRegExp = self.filterRegExp()
        if filterRegExp.isEmpty():
            return True

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, self.filteringColumn(), sourceParent)
        return filterRegExp.indexIn(sourceModel.data(indexBody)) != -1


class FnFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(0)
        self._enabled = False
        self._filterFn = None

    def filteringEnabled(self):
        return self._enabled

    def setFilteringEnabled(self, enabled: bool):
        self._enabled = enabled
        self.invalidateFilter()

    def filteringFn(self):
        return self._filterFn

    def setFilteringFn(self, fn: Callable[[str], bool]):
        self._filterFn = fn
        self._enabled = True
        self.invalidateFilter()

    def filteringColumn(self):
        return self.filterKeyColumn()

    def setFilteringColumn(self, column: int):
        self.setFilterKeyColumn(column)
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        if not self._enabled:
            return True

        sourceModel = self.sourceModel()
        index = sourceModel.index(sourceRow, self.filteringColumn(), sourceParent)
        return self._filterFn(sourceModel.data(index))
