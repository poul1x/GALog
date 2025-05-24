from typing import Optional

from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    pyqtSignal,
    Qt,
    QItemSelectionModel,
)
from PyQt5.QtGui import QFocusEvent, QKeyEvent
from PyQt5.QtWidgets import QListView, QWidget

from galog.app.ui.base.item_view_proxy import ItemViewProxy, ScrollHint

from ..helpers.hotkeys import HotkeyHelper
import logging


class BaseListView(QListView):
    #
    # This signal is used for cross-platform implementation of the 'activated' signal.
    # Unfortunately, the built-in implementation does not work on MacOS.
    # Therefore, we need to implement handlers for mouse double-click on a row and
    # keyboard shortcuts (<Enter>, <Space>) pressed on the selected row.
    #

    rowActivated = pyqtSignal(QModelIndex)

    def keyPressEvent(self, event: QKeyEvent):
        self._proxy.keyPressEvent(event)
        super().keyPressEvent(event)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._proxy = ItemViewProxy(self)

    def setModel(self, model: Optional[QAbstractItemModel]):
        self._proxy.setModel(model)
        super().setModel(model)
        self._proxy.updateFocusPolicy()

    def focusInEvent(self, e: QFocusEvent):
        self._proxy.focusInEvent(e)
        super().focusInEvent(e)

    def selectRow(self, row: int, scroll: Optional[ScrollHint] = None):
        self._proxy.selectRow(row, scroll)

    def selectNextRow(self):
        self._proxy.selectNextRow()

    def selectPrevRow(self):
        self._proxy.selectPrevRow()

    def selectRowByIndex(self, index: QModelIndex, scroll: Optional[ScrollHint] = None):
        self._proxy.selectRowByIndex(index, scroll)

    def selectedRows(self):
        return self._proxy.selectedRows()

    def hasItems(self):
        return self._proxy.hasItems()

    def hasSelectedItems(self):
        return self._proxy.hasSelectedItems()

    def trySetFocusAndGoUp(self):
        return self._proxy.trySetFocusAndGoUp()

    def trySetFocusAndGoDown(self):
        return self._proxy.trySetFocusAndGoDown()
