from __future__ import annotations

from typing import Any, List, Optional

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QWidget

# See https://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html


class TreeItem:
    _dataItems: List[str]
    _dataItemsEditable: List[bool]
    _children: List[TreeItem]
    _parent: Optional[TreeItem]

    def __init__(
        self,
        dataItems: List[str] = [],
        parent: Optional[TreeItem] = None,
    ) -> None:
        self._dataItemsEditable = [False for _ in range(len(dataItems))]
        self._dataItems = dataItems
        self._parent = parent
        self._children = []

    def isEditable(self, column: int):
        if column < 0 or column > len(self._dataItemsEditable):
            return False

        return self._dataItemsEditable[column]

    def setEditable(self, column: int, isEditable: bool):
        if column < 0 or column > len(self._dataItemsEditable):
            return False

        self._dataItemsEditable[column] = isEditable
        return True

    def data(self, column: int):
        if column < 0 or column > len(self._dataItems):
            return None

        return self._dataItems[column]

    def setData(self, column: int, data: str) -> bool:
        if column < 0 or column > len(self._dataItems):
            return False

        self._dataItems[column] = data
        return True

    def child(self, row: int):
        if row < 0 or row > len(self._children):
            return None

        return self._children[row]

    def addChild(self, item: TreeItem):
        item._parent = self
        self._children.append(item)

    def removeChild(self, item: TreeItem):
        item._parent = None
        self._children.remove(item)

    def removeChildren(self):
        for child in self._children:
            child._parent = None
        self._children.clear()

    def childCount(self):
        return len(self._children)

    def childIndex(self, item: TreeItem):
        return self._children.index(item)

    def row(self):
        if self._parent is None:
            return 0

        return self._parent.childIndex(self)

    def columnCount(self):
        return len(self._dataItems)

    def parentItem(self):
        return self._parent


class CustomTreeModel(QAbstractItemModel):
    _rootItem: TreeItem
    _numColumns: int

    def __init__(
        self,
        headers: TreeItem,
        parent: QWidget,
    ):
        super().__init__(parent)
        self._rootItem = headers
        self._numColumns = headers.columnCount()

    def setItems(self, treeItems: List[TreeItem]):
        self.layoutAboutToBeChanged.emit()

        self._rootItem.removeChildren()
        for item in treeItems:
            assert item.columnCount() == self._numColumns
            self._rootItem.addChild(item)

        # self.changePersistentIndex(
        #     self.createIndex(0, 0, self._rootItem),
        #     self.createIndex(self._rootItem.childCount(), 0, self._rootItem),
        # )

        self.layoutChanged.emit()

    def itemFromIndex(self, index: QModelIndex) -> TreeItem:
        if not index.isValid():
            return self._rootItem

        return index.internalPointer()

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem = self.itemFromIndex(parent)
        childItem = parentItem.child(row)

        if not childItem:
            return QModelIndex()

        return self.createIndex(row, column, childItem)

    def parent(self, index: QModelIndex) -> QModelIndex:
        childItem = self.itemFromIndex(index)
        parentItem = childItem.parentItem()

        if not parentItem or parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QModelIndex) -> int:
        if parent.column() > 0:
            return 0

        parentItem = self.itemFromIndex(parent)
        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex) -> int:
        return self._numColumns

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item: TreeItem = index.internalPointer()
        return item.data(index.column())

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        defaultFlags = super().flags(index)
        item = self.itemFromIndex(index)

        if item.isEditable(index.column()):
            return defaultFlags | Qt.ItemIsEditable

        return defaultFlags

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        if not value:
            return False

        item: TreeItem = index.internalPointer()
        return item.setData(index.column(), value)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._rootItem.data(section)

        return None
