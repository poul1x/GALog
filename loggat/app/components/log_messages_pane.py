from copy import copy
from random import randint
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.mtsearch import SearchItem, SearchItemTask, SearchResult

from loggat.app.util.painter import painterSaveRestore


class Columns(int, Enum):
    tagName = 0
    logLevel = 1
    logMessage = 2

class LazyHighlightingState(int, Enum):
    pending = 0
    running = 1
    done = 2

class CustomStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        if element == QStyle.PE_FrameFocusRect:
            # Do not draw the focus frame (dots) around selected items
            return
        super().drawPrimitive(element, option, painter, widget)

class HighlightingDelegate(QStyledItemDelegate):
    _items: List[List[SearchResult]]
    _tasks: List[bool]
    _ready: bool

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initTextDocument()
        self.rules = None
        self._items = []
        self._tasks = []
        self._background_selected = QColor("#DCDBFF")
        self._background_normal = QColor("#F2F2FF")

    def onNewLineAdded(self):
        self._items.append(list())
        self._tasks.append(LazyHighlightingState.pending)

    def clearHighlightingData(self):
        self._items.clear()
        self._tasks.clear()

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

    def searchDone(self, index: QModelIndex, results: List[SearchResult]):
        self._items[index.row()] = results
        self._tasks[index.row()] = LazyHighlightingState.done
        model = index.model()
        model.dataChanged.emit(index, index)


    def applyHighlighting(self, index: QModelIndex):

        if index.column() == Columns.logMessage:
            if self._tasks[index.row()] == LazyHighlightingState.running:
                return

            if self._tasks[index.row()] == LazyHighlightingState.done:
                self.highlightKeywords(index.row())
            else: # self._tasks[index.row()] == LazyHighlightingState.pending:
                items = []
                for name, pattern in self.rules.iter():
                    items.append(SearchItem(name, pattern))

                task = SearchItemTask(index.data(), items)
                task.signals.finished.connect(lambda results: self.searchDone(index, results))
                self._tasks[index.row()] = LazyHighlightingState.running
                QThreadPool.globalInstance().start(task)

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

        model = index.model()
        if isinstance(model, QSortFilterProxyModel):
            index = model.mapToSource(index)

        with painterSaveRestore(p) as painter:
            self.initStyleOption(viewItem, index)
            self.loadTextForHighlighting(viewItem)
            self.applyHighlighting(index)
            self.fillCellBackground(painter, viewItem)

            model = index.model()
            newIndex = model.index(
                index.row(), Columns.logLevel
            )  # Example: Get data from row 1, column 1
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


class CustomSortProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filteringEnabled = False

    def setFilteringEnabled(self, enabled: bool):
        self.filteringEnabled = enabled
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        if not self.filteringEnabled:
            return True

        filterRegExp = self.filterRegExp()
        if filterRegExp.isEmpty():
            return True

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, Columns.logMessage, sourceParent)
        return filterRegExp.indexIn(sourceModel.data(indexBody)) != -1


class LogMessagesPane(QWidget):

    """Displays log messages"""

    newLineAdded = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.initHighlightning()

    def initHighlightning(self):
        self._delegate = HighlightingDelegate(self._tableView)
        self.newLineAdded.connect(self._delegate.onNewLineAdded)
        self._tableView.setItemDelegate(self._delegate)

    def setHighlightingRules(self, rules: HighlightingRules):
        self._delegate.setHighlightingRules(rules)

    def initUserInterface(self):
        labels = ["Tag", "Log level", "Message"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        proxyModel = CustomSortProxyModel()
        proxyModel.setSourceModel(dataModel)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        tableView = QTableView(self)
        tableView.setModel(proxyModel)

        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)
        tableView.setColumnWidth(Columns.logLevel, 20)
        tableView.setColumnWidth(Columns.tagName, 200)
        tableView.setShowGrid(False)
        tableView.doubleClicked.connect(self.onDoubleClicked)
        tableView.setStyle(CustomStyle())

        hHeader = tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(False)
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setDefaultSectionSize(vHeader.minimumSectionSize())

        self._searchField = QLineEdit(self)
        self._searchField.setPlaceholderText("Search log message")
        self._searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)

        self._searchButton = QPushButton()
        self._searchButton.setText("Search")
        self._searchButton.clicked.connect(self.applyFilter)
        self._searchField.returnPressed.connect(self.applyFilter)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self._searchField)
        hLayout.addWidget(self._searchButton)
        self._searchButton.hide()
        self._searchField.hide()

        vLayout = QVBoxLayout()
        vLayout.addWidget(tableView)
        vLayout.addLayout(hLayout)

        self._tableView = tableView
        self._dataModel = dataModel
        self._proxyModel = proxyModel
        self.setLayout(vLayout)

        self.scrolling = True
        self._dataModel.rowsAboutToBeInserted.connect(self.beforeInsert)
        self._dataModel.rowsInserted.connect(self.afterInsert)

    def beforeInsert(self):
        vbar = self._tableView.verticalScrollBar()
        self._scrolling = vbar.value() == vbar.maximum()

    def afterInsert(self):
        if self._scrolling:
            self._tableView.scrollToBottom()


    def enableDisableFilter(self):

        # self._tableView.scrollTo(index, QTableView.PositionAtCenter)

        if self._proxyModel.filteringEnabled:
            self._proxyModel.setFilteringEnabled(False)
            self._tableView.verticalHeader().setVisible(False)
            self._searchButton.hide()
            self._searchField.hide()
        else:
            self._proxyModel.setFilteringEnabled(True)
            self._tableView.verticalHeader().setVisible(True)
            self._searchField.setFocus()
            self._searchButton.show()
            self._searchField.show()

    def applyFilter(self):
        self._proxyModel.setFilterFixedString(self._searchField.text())

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


    def onDoubleClicked(self, index: QModelIndex):
        if self._proxyModel.filteringEnabled:
            index2 = self._proxyModel.mapToSource(index)
            self.enableDisableFilter()

            self._tableView.scrollToBottom()
            index = self._proxyModel.index(index2.row(), 0)
            self._tableView.scrollTo(index, QTableView.PositionAtCenter)