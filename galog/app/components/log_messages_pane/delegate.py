from copy import copy
from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from PyQt5.QtCore import (
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
    QSize,
    QRectF,
)
from PyQt5.QtGui import (
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
from galog.app.util.colors import logLevelColor
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
        self._rules = None
        self._initFont()

    def setHighlightingRules(self, rules: HighlightingRules):
        self._rules = rules

    def _initFont(self):
        self._font = QFont()
        self._font.setFamily("Roboto Mono")
        self._font.setPixelSize(10)

        fm = QFontMetrics(self._font)
        self._fontHeight = fm.height()

    def _applyLogMessageHighlighting(self, doc: QTextDocument, index: QModelIndex):
        if index.column() != Columns.logMessage:
            return

        data: HighlightingData = index.data(Qt.UserRole)
        if data.state == LazyHighlightingState.running:
            return

        if data.state == LazyHighlightingState.done:
            self.highlightKeywords(doc, data.items)
            return

        # State is LazyHighlightingState.pending:
        data.state = LazyHighlightingState.running
        self.lazyHighlighting.emit(index)

    def _selectedRowHighlightCellText(
        self,
        doc: QTextDocument,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        if index.column() == Columns.logMessage:
            return

        if index.column() == Columns.logLevel:
            fmt = QTextCharFormat()
            fmt.setFontItalic(True)
            self.highlightAllText(doc, fmt)

        if option.state & QStyle.State_Selected:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.DemiBold)
            fmt.setFontItalic(True)
            self.highlightAllText(doc, fmt)

    def _selectedRowFillCellBackground(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        model = index.model()
        newIndex = model.index(index.row(), Columns.logLevel)
        inverted = model.data(newIndex, Qt.UserRole)
        logLevel = model.data(newIndex)

        if inverted:
            if option.state & QStyle.State_Selected:
                color = logLevelColor(logLevel)
            else:
                color = QColor("white")
        else:
            if option.state & QStyle.State_Selected:
                color = QColor("white")
            else:
                color = logLevelColor(logLevel)

        painter.fillRect(option.rect, color)

    def _drawCellContent(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        doc = QTextDocument()
        doc.setDefaultFont(self._font)
        doc.setProperty("elided", False)

        fm = QFontMetrics(self._font)
        textRect = option.widget.style().subElementRect(
            QStyle.SE_ItemViewItemText, option, option.widget
        )

        text = index.data()
        if fm.width(text) > textRect.width():
            text = fm.elidedText(text, Qt.ElideRight, textRect.width())
            doc.setProperty("elided", True)

        doc.setPlainText(text)
        self._applyLogMessageHighlighting(doc, index)
        self._selectedRowHighlightCellText(doc, option, index)
        self._selectedRowFillCellBackground(painter, option, index)

        padding = (option.rect.height() - fm.height()) // 2
        painter.translate(option.rect.left(), option.rect.top() + padding - 4)
        doc.drawContents(painter, QRectF(0, 0, textRect.width(), textRect.height()))

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        return QSize(0, self._fontHeight)

    def paint(self, p: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        if isinstance(model, QSortFilterProxyModel):
            index = model.mapToSource(index)

        with painterSaveRestore(p) as painter:
            self._drawCellContent(painter, option, index)

    def elidedTextLength(self, doc: QTextDocument):
        text = doc.toPlainText()
        length = doc.characterCount() - 1
        if text.endswith("..."):
            return length - 3
        elif text.endswith(".."):
            return length - 2
        elif text.endswith("."):
            return length - 1
        else:
            return length

    def textLength(self, doc: QTextDocument):
        if doc.property("elided") == True:
            return self.elidedTextLength(doc)
        else:
            return doc.characterCount() - 1

    def highlightKeywords(self, doc: QTextDocument, items: List[SearchResult]):
        textLength = self.textLength(doc)
        for item in items:
            if item.begin >= textLength:
                continue

            end = item.end
            if end >= textLength:
                end = textLength

            rule = self._rules.findRule(item.name)
            self.highlightKeyword(doc, rule.charFormat, item.begin, end)

    def highlightAllText(self, doc: QTextDocument, charFormat: QTextCharFormat):
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, doc: QTextDocument, begin: int, end: int):
        cursor = QTextCursor(doc)
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(
        self, doc: QTextDocument, charFormat: QTextCharFormat, begin: int, end: int
    ):
        cursor = self.cursorSelect(doc, begin, end)
        cursor.setCharFormat(charFormat)
