from copy import copy
from random import randint
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.mtsearch import SearchItemTask, SearchResult

from loggat.app.util.painter import painterSaveRestore


class Columns(int, Enum):
    tagName = 0
    logLevel = 1
    logMessage = 2


class HighlightingDelegate(QStyledItemDelegate):
    _items: List[List[SearchResult]]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initTextDocument()
        self.rules = None
        self._items = []
        self._background_selected = QColor("#DCDBFF")
        self._background_normal = QColor("#F2F2FF")

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
        viewItem.text = ""

    def applyHighlighting(self, index: QModelIndex):
        if index.column() == Columns.logMessage:
            self.highlightKeywords(index.row())

    def getStyle(self, viewItem: QStyleOptionViewItem):
        if viewItem.widget:
            return viewItem.widget.style()
        else:
            return QApplication.style()

    def fillCellBackground(self, painter: QPainter, viewItem: QStyleOptionViewItem):
        if viewItem.state & QStyle.State_Selected:
            painter.fillRect(viewItem.rect, self._background_selected)
        else:
            painter.fillRect(viewItem.rect, self._background_normal)

    def adjustCellText(self, painter: QPainter, viewItem: QStyleOptionViewItem):
        style = self.getStyle(viewItem)
        style.drawControl(QStyle.CE_ItemViewItem, viewItem, painter)
        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, viewItem)

        margin = (viewItem.rect.height() - viewItem.fontMetrics.height()) // 2
        textRect.setTop(textRect.top() + margin - 4)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))

    def drawCell(self, painter: QPainter):
        ctx = QAbstractTextDocumentLayout.PaintContext()
        self.doc.documentLayout().draw(painter, ctx)

    def paint(self, p: QPainter, viewItem: QStyleOptionViewItem, index: QModelIndex):

        # model = index.model()
        # if isinstance(model, QSortFilterProxyModel):
        #     index = model.mapToSource(index)

        with painterSaveRestore(p) as painter:
            self.initStyleOption(viewItem, index)
            self.loadTextForHighlighting(viewItem)
            self.applyHighlighting(index)
            self.fillCellBackground(painter, viewItem)

            model = index.model()
            newIndex = model.index(index.row(), Columns.logLevel)  # Example: Get data from row 1, column 1
            data = model.data(newIndex, role=Qt.DisplayRole)

            if data == "E":
                color = QColor("#FF2635")
                color.setAlphaF(0.4)
            elif data == "I":
                color = QColor("#C7CFFF")
            elif data == "W":
                color = QColor("#FFBC00")
                color.setAlphaF(0.5)
            elif data == "D":
                color = QColor("green")
                color.setAlphaF(0.4)
            else:
                color = QColor("orange")
                color.setAlphaF(0.4)

            painter.fillRect(viewItem.rect, color)

            self.adjustCellText(painter, viewItem)
            self.drawCell(painter)

    def highlightKeywords(self, row: int):
        n = self.doc.characterCount() - 2
        for item in self._items[row]:
            style = self.rules.getStyle(item.name)

            itemCopy = copy(item)
            if itemCopy.begin >= n:
                continue

            if itemCopy.end > n + 1:
                itemCopy.end = n

            self.highlightKeyword(itemCopy, style)

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self.doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self.doc)
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: SearchResult, charFormat: QTextCharFormat):
        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)


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
        labels = ["Tag", "Log level", "Message"]
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

        row = [itemTagName, itemLogLevel, itemLogMessage]
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
