from typing import Optional

from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    pyqtBoundSignal,
    Qt,
    QItemSelectionModel,
)
from PyQt5.QtGui import QFocusEvent, QKeyEvent
from PyQt5.QtWidgets import QListView, QWidget, QAbstractItemView

from ..helpers.hotkeys import HotkeyHelper
import logging


class ItemViewProxy:
    _rowActivatedSignal: pyqtBoundSignal

    def _emitRowActivated(self, index: QModelIndex):
        msg = "Row activated: row=%d, column=%d"
        self._logger.debug(msg, index.row(), index.column())
        self._rowActivatedSignal.emit(index)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEnterPressed() or helper.isSpacePressed():
            indexes = self._itemView.selectionModel().selectedIndexes()
            if indexes:
                self._emitRowActivated(indexes[0])

    def __init__(self, itemView: QAbstractItemView):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info("ItemViewProxy created")
        assert hasattr(itemView, "rowActivated"), "Must have rowActivated signal"
        self._rowActivatedSignal = getattr(itemView, "rowActivated")
        itemView.doubleClicked.connect(self._emitRowActivated)
        self._itemView = itemView

    def updateFocusPolicy(self):
        if self._itemView.model().rowCount() == 0:
            self._logger.debug("setFocusPolicy to NoFocus")
            self._itemView.setFocusPolicy(Qt.NoFocus)
        else:
            self._logger.debug("setFocusPolicy to StrongFocus")
            self._itemView.setFocusPolicy(Qt.StrongFocus)

    def setModel(self, model: QAbstractItemModel):
        self._logger.info("setModel: add 'updateFocusPolicy' callback")
        model.rowsInserted.connect(self.updateFocusPolicy)
        model.rowsRemoved.connect(self.updateFocusPolicy)

    def focusInEvent(self, e: QFocusEvent):
        if not self.hasItems():
            self._logger.debug("focusInEvent: no items")
            return

        if self.hasSelectedItems():
            self._logger.debug("focusInEvent: has selected items")
            return

        self._logger.debug("focusInEvent: select first row")
        self.selectRow(0)

    def selectRow(self, row: int):
        model = self._itemView.model()
        if row < 0 or row >= model.rowCount():
            return False

        index = model.index(row, 0)
        self.selectRowByIndex(index)
        return True

    def selectNextRow(self):
        index = self._itemView.currentIndex()
        assert index.isValid(), "Index must be valid"
        return self.selectRow(index.row() + 1)

    def selectPrevRow(self):
        index = self._itemView.currentIndex()
        assert index.isValid(), "Index must be valid"
        return self.selectRow(index.row() - 1)

    def selectRowByIndex(self, index: QModelIndex):
        assert index.isValid(), "Index must be valid"
        self._itemView.setCurrentIndex(index)

        flags = QItemSelectionModel.Select | QItemSelectionModel.Rows
        selectionModel = self._itemView.selectionModel()
        selectionModel.select(index, flags)

        # self._itemView.scrollTo(index, QAbstractItemView.PositionAtCenter)

    def selectedRows(self):
        def key(index: QModelIndex):
            return index.row()

        selectionModel = self._itemView.selectionModel()
        selectedRows = sorted(selectionModel.selectedRows(), key=key, reverse=True)
        return [index.row() for index in selectedRows]

    def hasItems(self):
        return self._itemView.model().rowCount() > 0

    def hasSelectedItems(self):
        return bool(self._itemView.selectedIndexes())

    def trySetFocusAndGoUp(self):
        # ListView does not have items
        # -> do not set focus
        if not self.hasItems():
            return

        # ListView has items, but nothing selected
        # -> set focus (automatically selects first row)
        if not self.hasSelectedItems():
            self._itemView.setFocus()
            return

        # ListView has items and something selected
        # -> set focus (something remains selected)
        # and select previous row to emit "Go Up" behavior
        self._itemView.setFocus()
        self.selectPrevRow()

    def trySetFocusAndGoDown(self):
        # ListView does not have items
        # -> do not set focus
        if not self.hasItems():
            return

        # ListView has items, but nothing selected
        # -> set focus (automatically selects first row)
        if not self.hasSelectedItems():
            self._itemView.setFocus()
            return

        # ListView has items and something selected
        # -> set focus (something remains selected)
        # and select next row to emit "Go Down" behavior
        self._itemView.setFocus()
        self.selectNextRow()
