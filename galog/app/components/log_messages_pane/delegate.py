from copy import copy
from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel, Qt, pyqtSignal
from PyQt5.QtGui import (
    QAbstractTextDocumentLayout,
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PyQt5.QtWidgets import *

from galog.app.controllers.log_messages_pane.search import SearchResult
from galog.app.highlighting import HighlightingRules
from galog.app.util.painter import painterSaveRestore

from .data_model import Columns


class LazyHighlightingState(int, Enum):
    pending = auto()
    running = auto()
    done = auto()


@dataclass
class HighlightingData:
    state: LazyHighlightingState
    items: List[SearchResult]


class StyledItemDelegate(QStyledItemDelegate):
    lazyHighlighting = pyqtSignal(QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initTextDocument()
        self._rules = None

    def sizeHint(self, viewItem: QStyleOptionViewItem, index: QModelIndex):
        return QStyledItemDelegate.sizeHint(self, viewItem, index)

    def setHighlightingRules(self, rules: HighlightingRules):
        self._rules = rules

    def _initTextDocument(self):
        font = QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(10)
        self._doc = QTextDocument(self)
        self._doc.setDefaultFont(font)

    def setTextForDisplay(self, viewItem: QStyleOptionViewItem):
        fm = QFontMetrics(self._doc.defaultFont())
        elidedText = fm.elidedText(viewItem.text, Qt.ElideRight, viewItem.rect.width())
        self._doc.setPlainText(elidedText)
        viewItem.text = ""

    def highlightSelectedRow(self, viewItem: QStyleOptionViewItem, index: QModelIndex):
        if index.column() != Columns.logMessage:
            if viewItem.state & QStyle.State_Selected:
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.DemiBold)
                self.highlightAllText(fmt)

    def applyHighlighting(self, index: QModelIndex):
        if index.column() != Columns.logMessage:
            return

        data: HighlightingData = index.data(Qt.UserRole)
        if data.state == LazyHighlightingState.running:
            return

        if data.state == LazyHighlightingState.done:
            self.highlightKeywords(data.items)
            return

        # data.state == LazyHighlightingState.pending:
        data.state = LazyHighlightingState.running
        self.lazyHighlighting.emit(index)

    def style(self, viewItem: QStyleOptionViewItem):
        if viewItem.widget:
            return viewItem.widget.style()
        else:
            return QApplication.style()

    def fillCellBackground(
        self,
        index: QModelIndex,
        viewItem: QStyleOptionViewItem,
        painter: QPainter,
    ):
        model = index.model()
        newIndex = model.index(index.row(), Columns.logLevel)
        inverted = model.data(newIndex, Qt.UserRole)
        logLevel = model.data(newIndex)

        if inverted:
            if viewItem.state & QStyle.State_Selected:
                color = self.rowColor(logLevel)
                painter.fillRect(viewItem.rect, color)
            else:
                color = self.rowColorSelected(logLevel)
                painter.fillRect(viewItem.rect, color)
        else:
            if viewItem.state & QStyle.State_Selected:
                color = self.rowColorSelected(logLevel)
                painter.fillRect(viewItem.rect, color)
            else:
                color = self.rowColor(logLevel)
                painter.fillRect(viewItem.rect, color)

    def draw(self, viewItem: QStyleOptionViewItem, painter: QPainter):
        style = self.style(viewItem)
        style.drawControl(QStyle.CE_ItemViewItem, viewItem, painter)
        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, viewItem)

        margin = (viewItem.rect.height() - viewItem.fontMetrics.height()) // 2
        textRect.setTop(textRect.top() + margin - 4)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))

        ctx = QAbstractTextDocumentLayout.PaintContext()
        self._doc.documentLayout().draw(painter, ctx)

    def rowColorSelected(self, logLevel: str):
        return QColor("white")

    def rowColor(self, logLevel: str):
        if logLevel == "F":
            color = QColor("#FF2635")
            color.setAlphaF(0.4)
        elif logLevel == "E":
            color = QColor("#FF2635")
            color.setAlphaF(0.4)
        elif logLevel == "I":
            color = QColor("#C7CFFF")
        elif logLevel == "W":
            color = QColor("#FFBC00")
            color.setAlphaF(0.5)
        elif logLevel == "D":
            color = QColor("green")
            color.setAlphaF(0.4)
        elif logLevel == "V":
            color = QColor("orange")
            color.setAlphaF(0.4)
        else:  # logLevel == "S"
            color = QColor("#FFFFFF")

        return color

    def paint(self, p: QPainter, viewItem: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        if isinstance(model, QSortFilterProxyModel):
            index = model.mapToSource(index)

        with painterSaveRestore(p) as painter:
            self.initStyleOption(viewItem, index)
            self.fillCellBackground(index, viewItem, painter)
            self.setTextForDisplay(viewItem)
            self.highlightSelectedRow(viewItem, index)
            self.applyHighlighting(index)
            self.draw(viewItem, painter)

    def highlightKeywords(self, items: List[SearchResult]):
        n = self._doc.characterCount() - 2
        for item in items:
            itemCopy = copy(item)
            if itemCopy.begin >= n:
                continue

            if itemCopy.end > n + 1:
                itemCopy.end = n

            rule = self._rules.findRule(item.name)
            self.highlightKeyword(itemCopy, rule.charFormat)

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self._doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self._doc)
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: SearchResult, charFormat: QTextCharFormat):
        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)
