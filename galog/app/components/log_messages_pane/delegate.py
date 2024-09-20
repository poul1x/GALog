from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from PySide6.QtCore import QModelIndex, QRectF, QSortFilterProxyModel, Qt, Signal
from PySide6.QtGui import (
    QFont,
    QFontMetrics,
    QPainter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from galog.app.controllers.log_messages_pane.search import SearchResult
from galog.app.highlighting import HighlightingRules
from galog.app.util.colors import logLevelColor, rowSelectedColor
from galog.app.util.painter import painterSaveRestore

from .data_model import Column


class LazyHighlightingState(int, Enum):
    pending = auto()
    running = auto()
    done = auto()


@dataclass
class HighlightingData:
    state: LazyHighlightingState
    items: List[SearchResult]


class StyledItemDelegate(QStyledItemDelegate):
    lazyHighlighting = Signal(QModelIndex)
    _highlightingEnabled: bool

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = None
        self._highlightingEnabled = True
        self._initFont()

    def setFont(self, font: QFont):
        self._font = font

    def font(self):
        return self._font

    def setHighlightingRules(self, rules: HighlightingRules):
        self._rules = rules

    def setHighlightingEnabled(self, enabled: bool):
        self._highlightingEnabled = enabled

    def highlightingEnabled(self):
        return self._highlightingEnabled

    def _initFont(self):
        self._font = QFont()
        self._font.setFamily("Roboto Mono")
        self._font.setPixelSize(14)

    def _applyLogMessageHighlighting(self, doc: QTextDocument, index: QModelIndex):
        if index.column() != Column.logMessage:
            return

        if not self._highlightingEnabled:
            return

        data: HighlightingData = index.data(Qt.ItemDataRole.UserRole)
        if data.state == LazyHighlightingState.done:
            self.highlightKeywords(doc, data.items)
        elif data.state == LazyHighlightingState.pending:
            data.state = LazyHighlightingState.running
            self.lazyHighlighting.emit(index)
        else:  # data.state == LazyHighlightingState.running:
            pass

    def _selectedRowHighlightCellText(
        self,
        doc: QTextDocument,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        if index.column() == Column.logMessage:
            return

        if index.column() == Column.logLevel:
            fmt = QTextCharFormat()
            fmt.setFontItalic(True)
            self.highlightAllText(doc, fmt)

        if option.state & QStyle.StateFlag.State_Selected:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.DemiBold)
            fmt.setFontItalic(True)
            self.highlightAllText(doc, fmt)

    def _selectedRowFillCellBackground(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        model = index.model()
        newIndex = model.index(index.row(), Column.logLevel)
        inverted = model.data(newIndex, Qt.ItemDataRole.UserRole)
        logLevel = model.data(newIndex)

        if inverted:
            if option.state & QStyle.StateFlag.State_Selected:
                color = logLevelColor(logLevel)
            else:
                color = rowSelectedColor()
        else:
            if option.state & QStyle.StateFlag.State_Selected:
                color = rowSelectedColor()
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
            QStyle.SubElement.SE_ItemViewItemText, option, option.widget
        )

        text = index.data()
        if fm.horizontalAdvance(text) > textRect.width():
            text = fm.elidedText(text, Qt.TextElideMode.ElideRight, textRect.width())
            doc.setProperty("elided", True)

        doc.setPlainText(text)
        self._applyLogMessageHighlighting(doc, index)
        self._selectedRowHighlightCellText(doc, option, index)
        self._selectedRowFillCellBackground(painter, option, index)

        padding = (option.rect.height() - fm.height()) // 2
        painter.translate(option.rect.left(), option.rect.top() + padding - 4)
        doc.drawContents(painter, QRectF(0, 0, textRect.width(), textRect.height()))

    def paint(self, p: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        assert self._font is not None
        assert self._rules is not None

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
            if end > textLength:
                end = textLength - 1

            rule = self._rules.findRule(item.name)
            groupNum = item.groupNum

            charFormat = rule.match
            if groupNum != 0:
                charFormat = rule.groups[groupNum]

            self.highlightKeyword(doc, charFormat, item.begin, end)

    def highlightAllText(self, doc: QTextDocument, charFormat: QTextCharFormat):
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, doc: QTextDocument, begin: int, end: int):
        cursor = QTextCursor(doc)
        cursor.setPosition(begin, QTextCursor.MoveMode.MoveAnchor)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        return cursor

    def highlightKeyword(
        self, doc: QTextDocument, charFormat: QTextCharFormat, begin: int, end: int
    ):
        cursor = self.cursorSelect(doc, begin, end)
        cursor.setCharFormat(charFormat)
