from typing import Optional
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex, QRect, QRect
from PyQt5.QtGui import QKeyEvent, QPainter, QColor, QTextDocument, QFont, QPen
from PyQt5.QtWidgets import QTableView, QWidget, QAbstractItemView, QHeaderView, QStyle, QStyleOptionViewItem
from galog.app.highlighting import HighlightingRules
from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.painter import painterSaveRestore

from .data_model import Columns
from .delegate import StyledItemDelegate

class VerticalHeader(QHeaderView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Vertical, parent)
        self._font = QFont()
        self._font.setPixelSize(20)
        self._font.setFamily("Arial")
        self._font.setWeight(QFont.Bold)

    def _selectedRows(self):
        return [index.row() for index in self.selectionModel().selectedRows()]

    def paintSection(self, _painter: QPainter, rect: QRect, index: int):
        align = Qt.AlignCenter
        lightColor = QColor("#FFFFFF")
        darkColor = QColor("#464646")

        with painterSaveRestore(_painter) as painter:
            if index in self._selectedRows():
                painter.fillRect(rect, darkColor)
                painter.setPen(lightColor)
            else:
                painter.fillRect(rect, lightColor)
                painter.setPen(darkColor)

            painter.setFont(self._font)
            painter.drawText(rect, align, str(index + 1))



class TableView(QTableView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.delegate = StyledItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.initUserInterface()

    def initUserInterface(self):
        self.setCornerButtonEnabled(False)
        self.setVerticalHeader(VerticalHeader(self))
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)
