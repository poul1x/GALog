from copy import copy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.color_parser import HighlightingRules
from loggat.app.mtsearch import SearchItemTask, SearchResult

from loggat.app.util.painter import painterSaveRestore


class Columns(int, Enum):
    logLevel = 0
    tagName = 1
    logMessage = 2


class Highlighter:
    def __init__(self, index: QModelIndex, doc: QTextDocument) -> None:
        self.doc = doc

    def highlightColumnText(self, index: QModelIndex):
        pass

    def highlightLogLevel(self, logLevel: str):
        self.doc.setPlainText(logLevel)
        char_format = QTextCharFormat()
        char_format.setForeground(Qt.red)  # Set the font color to red
        cursor = QTextCursor(self.doc)
        cursor.select(QTextCursor.Document)
        cursor.mergeCharFormat(char_format)

    def logMessageTextDefaultFormatting(self):
        # Set the color for the entire text
        char_format = QTextCharFormat()
        char_format.setForeground(Qt.red)  # Set the font color to red
        cursor = QTextCursor(self.doc)
        cursor.select(QTextCursor.Document)
        cursor.mergeCharFormat(char_format)

    def apply_highlight(self):
        cursor = QTextCursor(self.doc)
        cursor.beginEditBlock()
        fmt = QTextCharFormat()
        fmt.setForeground(Qt.red)
        fmt.setFontWeight(QFont.Bold)
        fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        # fmt.setFontPointSize(12)
        fmt.setAnchor(True)
        for f in ["12345"]:
            highlightCursor = QTextCursor(self.doc)
            while not highlightCursor.isNull() and not highlightCursor.atEnd():
                highlightCursor = self.doc.find(f, highlightCursor)
                if not highlightCursor.isNull():
                    highlightCursor.mergeCharFormat(fmt)
        cursor.endEditBlock()


class HighlightingDelegate(QStyledItemDelegate):
    _items: List[SearchResult]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initTextDocument()
        self.rules = None
        self._items = []

    def onLineHighlightingReady(self, row: int, items: List[SearchResult]):
        self._items[row] = items

    def onNewLineAdded(self):
        self._items.append(list())

    def clearHighlightingData(self):
        self._items.clear()

    def setHighlightingRules(self, rules: HighlightingRules):
        self.rules = rules

    def setItemsToHighlight(self, items: list):
        self._items = items

    def _initTextDocument(self):
        font = QFont()
        font.setPointSize(10)
        self.doc = QTextDocument(self)
        self.doc.setDefaultFont(font)

    def loadTextForHighlighting(self, viewItem: QStyleOptionViewItem):
        fm = QFontMetrics(self.doc.defaultFont())
        elidedText = fm.elidedText(viewItem.text, Qt.ElideRight, viewItem.rect.width())
        self.doc.setPlainText(elidedText)

    def applyHighlighting(self, index: QModelIndex):
        if index.column() == Columns.tagName:
            self.highlightTag(index.data())
            return
        if index.column() == Columns.logLevel:
            self.highlightLogLevel(index.data())
            return
        else:
            plainText = self.doc.toPlainText()
            n = 2
            if plainText.endswith("..."):
                n = 3

            n = self.doc.characterCount() - n
            row = index.row()
            items = self._items[row]
            item: SearchResult
            for item in items:
                style = self.rules.getStyle(item.name)
                itemCopy = copy(item)

                if itemCopy.begin < n:
                    if itemCopy.end > n:
                        itemCopy.end = n
                    self.highlightKeyword(itemCopy, style)
            return

    def getStyle(self, viewItem: QStyleOptionViewItem):
        if viewItem.widget:
            return viewItem.widget.style()
        else:
            return QApplication.style()

    def _paint(
        self,
        painter: QPainter,
        viewItem: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        self.initStyleOption(viewItem, index)
        self.loadTextForHighlighting(viewItem)
        self.applyHighlighting(index)
        viewItem.text = ""

        style = self.getStyle(viewItem)
        style.drawControl(QStyle.CE_ItemViewItem, viewItem, painter)

        if viewItem.state & QStyle.State_Selected:
            painter.fillRect(viewItem.rect, QColor("#DCDBFF"))
        else:
            painter.fillRect(viewItem.rect, QColor("#F2F2FF"))

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, viewItem)
        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)

        the_constant = 4
        margin = (viewItem.rect.height() - viewItem.fontMetrics.height()) // 2
        margin = margin - the_constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))

        ctx = QAbstractTextDocumentLayout.PaintContext()
        self.doc.documentLayout().draw(painter, ctx)

    def paint(
        self,
        painter: QPainter,
        viewItem: QStyleOptionViewItem,
        index: QModelIndex,
    ):
        with painterSaveRestore(painter) as p:
            self._paint(p, viewItem, index)

    def highlightLogLevel(self, logLevel: str):
        logLevel = logLevel.upper()
        charFormat = QTextCharFormat()
        charFormat.setFontWeight(QFont.Bold)

        if logLevel == "I":
            charFormat.setForeground(QColor("#DCDCDC"))
        elif logLevel == "E":
            charFormat.setForeground(QColor("#FF5454"))
        else:
            charFormat.setForeground(QColor("#6352B9"))

        self.highlightAllText(charFormat)

    def highlightTag(self, tag: str):
        tag = tag.lower()
        charFormat = QTextCharFormat()

        if tag == "dalvikvm":
            charFormat.setForeground(QColor("#DCDCDC"))
            charFormat.setBackground(QColor("#2E2D2D"))
        elif tag == "process":
            charFormat.setForeground(QColor("#FF5454"))
            charFormat.setBackground(QColor("#EBEBEB"))
        # else:
        #     charFormat.setForeground(QColor("#6352B9"))
        #     charFormat.setBackground(QColor("#EBEBEB"))

        # 'Process' 'ActivityManager' 'ActivityThread' 'AndroidRuntime' 'jdwp' 'StrictMode' 'DEBUG'
        self.highlightAllText(charFormat)

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self.doc)
        cursor.select(QTextCursor.Document)
        cursor.mergeCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self.doc)
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: SearchResult, charFormat: QTextCharFormat):
        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.mergeCharFormat(charFormat)


class LogMessagesPane(QWidget):

    """Displays log messages"""

    lineHighlightingReady = pyqtSignal(int, list)
    newLineAdded = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.initHighlightning()

    def initHighlightning(self):
        self._delegate = HighlightingDelegate(self)
        self.lineHighlightingReady.connect(self._delegate.onLineHighlightingReady)
        self.newLineAdded.connect(self._delegate.onNewLineAdded)
        self._tableView.setItemDelegate(self._delegate)

    def setHighlightingRules(self, rules: HighlightingRules):
        self._delegate.setHighlightingRules(rules)

    def initUserInterface(self):
        labels = ["Log level", "Tag", "Message"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        tableView = QTableView(self)
        tableView.setModel(dataModel)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)
        tableView.setColumnWidth(Columns.logLevel, 20)
        tableView.setColumnWidth(Columns.tagName, 200)
        tableView.setShowGrid(False)

        hHeader = tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(False)
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setDefaultSectionSize(vHeader.minimumSectionSize())

        layout = QVBoxLayout()
        layout.addWidget(tableView)

        self._tableView = tableView
        self._dataModel = dataModel
        self.setLayout(layout)

        self._scroll = True
        self._dataModel.rowsAboutToBeInserted.connect(self.beforeInsert)
        self._dataModel.rowsInserted.connect(self.afterInsert)

    def beforeInsert(self):
        vbar = self._tableView.verticalScrollBar()
        self._scroll = vbar.value() == vbar.maximum()

    def afterInsert(self):
        if self._scroll:
            self._tableView.scrollToBottom()

    def clear(self):
        self._dataModel.clear()

    def appendRow(self, logLevel, tagName, logMessage):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        itemLogLevel = QStandardItem(logLevel)
        itemLogLevel.setFlags(flags)

        itemTagName = QStandardItem(tagName)
        itemTagName.setFlags(flags)

        itemLogMessage = QStandardItem(logMessage)
        itemLogMessage.setFlags(flags)

        row = [itemLogLevel, itemTagName, itemLogMessage]
        self._dataModel.appendRow(row)
        self.newLineAdded.emit()

    def onLineHighlightingReady(self, row: int, items: List[SearchResult]):
        self.lineHighlightingReady.emit(row, items)
        index = self._dataModel.createIndex(row, Columns.logMessage)
        self._tableView.update(index)

    def navigateToItem(self, row, col):
        self.activateWindow()
        self.raise_()
        if (
            0 <= row < self._dataModel.rowCount()
            and 0 <= col < self._dataModel.columnCount()
        ):
            self._tableView.selectRow(row)
