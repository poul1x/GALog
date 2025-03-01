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

from ..helpers.hotkeys import HotkeyHelper
import logging


class ListView(QListView):
    #
    # This widget is used for cross-platform implementation of the 'activated' signal.
    # Unfortunately, the built-in implementation does not work on MacOS.
    # Therefore, we need to implement handlers for mouse double-click on a row and
    # keyboard shortcuts (<Enter>, <Space>) pressed on the selected row.
    #

    rowActivated = pyqtSignal(QModelIndex)

    def _emitRowActivated(self, index: QModelIndex):
        msg = "Row activated: row=%d, column=%d"
        self._logger.debug(msg, index.row(), index.column())
        self.rowActivated.emit(index)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEnterPressed() or helper.isSpacePressed():
            indexes = self.selectionModel().selectedIndexes()
            if indexes:
                self._emitRowActivated(indexes[0])

        return super().keyPressEvent(event)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doubleClicked.connect(self._emitRowActivated)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info("ListView created")

    def _updateFocusPolicy(self):
        if self.model().rowCount() == 0:
            self._logger.debug("setFocusPolicy to NoFocus")
            self.setFocusPolicy(Qt.NoFocus)
        else:
            self._logger.debug("setFocusPolicy to StrongFocus")
            self.setFocusPolicy(Qt.StrongFocus)

    def setModel(self, model: Optional[QAbstractItemModel]):
        self._logger.info("setModel: add 'updateFocusPolicy' callback")
        model.rowsInserted.connect(self._updateFocusPolicy)
        model.rowsRemoved.connect(self._updateFocusPolicy)
        super().setModel(model)
        self._updateFocusPolicy()

    def focusInEvent(self, e: QFocusEvent):
        if not self.hasItems():
            self._logger.debug("focusInEvent: no items")
            return

        if self.hasSelectedItems():
            self._logger.debug("focusInEvent: has selected items")
            return

        self._logger.debug("focusInEvent: select first row")
        self.selectRow(0)

        return super().focusInEvent(e)

    def selectRow(self, row: int):
        model = self.model()
        if row < 0 or row >= model.rowCount():
            return False

        index = model.index(row, 0)
        self.selectRowByIndex(index)
        return True

    def selectNextRow(self):
        index = self.currentIndex()
        assert index.isValid(), "Index must be valid"
        return self.selectRow(index.row() + 1)

    def selectPrevRow(self):
        index = self.currentIndex()
        assert index.isValid(), "Index must be valid"
        return self.selectRow(index.row() - 1)

    def selectRowByIndex(self, index: QModelIndex):
        assert index.isValid(), "Index must be valid"
        self.setCurrentIndex(index)

        selectionModel = self.selectionModel()
        selectionModel.select(index, QItemSelectionModel.Select)

        self.scrollTo(index, QListView.PositionAtCenter)

    def selectedRows(self):
        def key(index: QModelIndex):
            return index.row()

        selectionModel = self.selectionModel()
        selectedRows = sorted(selectionModel.selectedRows(), key=key, reverse=True)
        return [index.row() for index in selectedRows]

    def hasItems(self):
        return self.model().rowCount() > 0

    def hasSelectedItems(self):
        return bool(self.selectedIndexes())

    def _trySetFocusAndGoUpDown(self):
        if not self.hasItems():
            return False

        hasSelectedItems = self.hasSelectedItems()
        self.setFocus()

        return hasSelectedItems

    def trySetFocus(self):
        if self.hasItems():
            self.setFocus()

    def trySetFocusAndGoUp(self):
        if self._trySetFocusAndGoUpDown():
            self.selectPrevRow()

    def trySetFocusAndGoDown(self):
        if self._trySetFocusAndGoUpDown():
            self.selectNextRow()
