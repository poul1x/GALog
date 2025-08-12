from typing import List, Optional

from PyQt5.QtCore import QModelIndex, QRectF, Qt, QThreadPool, QObject
from PyQt5.QtGui import (
    QFont,
    QFontMetrics,
    QPainter,
    QStandardItemModel,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PyQt5.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from galog.app.hrules import HRulesStorage
from galog.app.settings.notifier import ChangedEntry, SettingsChangeNotifier
from galog.app.settings.settings import readSettings
from galog.app.ui.core.log_messages_panel.log_messages_table.colors import (
    logLevelColor,
    rowSelectedColor,
)
from galog.app.ui.helpers.painter import painterSaveRestore

from .data_model import Column, HighlightingData, LazyHighlightingState
from .pattern_search_task import (
    PatternSearchItem,
    PatternSearchResult,
    PatternSearchTask,
)
from .row_blinking_animation import RowBlinkingAnimation


class LogLineDelegate(QStyledItemDelegate):
    _highlightingEnabled: bool

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._rowBlinkingAnimation = None
        self._highlightingEnabled = True
        self._highlightingRules = None

    def font(self):
        assert self._font is not None
        return self._font

    def setFont(self, font: QFont):
        self._font = font

    def highlightingRules(self):
        return self._highlightingRules

    def setHighlightingRules(self, rules: HRulesStorage):
        self._highlightingRules = rules

    def setHighlightingEnabled(self, enabled: bool):
        self._highlightingEnabled = enabled

    def highlightingEnabled(self):
        return self._highlightingEnabled

    def _applyLogMessageHighlighting(self, doc: QTextDocument, index: QModelIndex):
        if index.column() != Column.logMessage:
            return

        if not self._highlightingEnabled or self._highlightingRules is None:
            return

        data: HighlightingData = index.data(Qt.UserRole)
        if data.state == LazyHighlightingState.pending:
            data.state = LazyHighlightingState.running
            self._startLazyHighlightingTask(index)
            return

        if data.state == LazyHighlightingState.running:
            return

        assert data.state == LazyHighlightingState.done
        self._highlightKeywords(doc, data.items)

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
            self._highlightAllText(doc, fmt)

        if option.state & QStyle.State_Selected:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.DemiBold)
            fmt.setFontItalic(True)
            self._highlightAllText(doc, fmt)

    def _selectedRowFillCellBackground(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        model = index.model()
        logLevel = model.index(index.row(), Column.logLevel).data()

        inverted = False
        if self._rowBlinkingAnimation is not None:
            animatedRow = self._rowBlinkingAnimation.row()
            if index.row() == animatedRow:
                inverted = self._rowBlinkingAnimation.colorInverted()

        if inverted:
            if option.state & QStyle.State_Selected:
                color = logLevelColor(logLevel)
            else:
                color = rowSelectedColor()
        else:
            if option.state & QStyle.State_Selected:
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
        doc.setDefaultFont(self.font())
        doc.setProperty("elided", False)

        fm = QFontMetrics(self.font())
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

    def paint(self, p: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        with painterSaveRestore(p) as painter:
            self._drawCellContent(painter, option, index)

    def _elidedTextLength(self, doc: QTextDocument):
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

    def _textLength(self, doc: QTextDocument):
        if doc.property("elided") == True:
            return self._elidedTextLength(doc)
        else:
            return doc.characterCount() - 1

    def _highlightKeywords(self, doc: QTextDocument, items: List[PatternSearchResult]):
        textLength = self._textLength(doc)
        for item in items:
            if item.begin >= textLength:
                continue

            end = item.end
            if end > textLength:
                end = textLength - 1

            rule = self._highlightingRules.findRule(item.name)
            groupNum = item.groupNum

            charFormat = rule.match
            if groupNum != 0:
                charFormat = rule.groups[groupNum]

            self._highlightKeyword(doc, charFormat, item.begin, end)

    def _highlightAllText(self, doc: QTextDocument, charFormat: QTextCharFormat):
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def _cursorSelect(self, doc: QTextDocument, begin: int, end: int):
        cursor = QTextCursor(doc)
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def _highlightKeyword(
        self, doc: QTextDocument, charFormat: QTextCharFormat, begin: int, end: int
    ):
        cursor = self._cursorSelect(doc, begin, end)
        cursor.setCharFormat(charFormat)

    def _lazyHighlightingDataReady(
        self, index: QModelIndex, results: List[PatternSearchResult]
    ):
        data = HighlightingData(
            state=LazyHighlightingState.done,
            items=results,
        )

        model = index.model()
        model.setData(index, data, Qt.UserRole)
        model.dataChanged.emit(index, index)

    def _startLazyHighlightingTask(self, index: QModelIndex):
        assert self._highlightingRules is not None
        assert index.column() == Column.logMessage

        items = []
        for name, rule in self._highlightingRules.items():
            groups = set()
            if rule.match:
                groups.add(0)
            if rule.groups:
                groups.update(rule.groups.keys())

            item = PatternSearchItem(name, rule.pattern, rule.priority, groups)
            items.append(item)

        task = PatternSearchTask(index.data(), items)
        onFinished = lambda results: self._lazyHighlightingDataReady(index, results)
        task.signals.finished.connect(onFinished)
        QThreadPool.globalInstance().start(task)

    def startRowBlinking(self, row: int, model: QStandardItemModel):
        self._rowBlinkingAnimation = RowBlinkingAnimation(row, model)
        self._rowBlinkingAnimation.finished.connect(self._deleteAnimation)
        self._rowBlinkingAnimation.startBlinking()

    def _deleteAnimation(self):
        self._rowBlinkingAnimation = None
