from copy import copy
from random import randint
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum, auto

from PyQt5.QtWidgets import QWidget
from loggat.app.components.message_view_pane import LogMessageViewPane
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.mtsearch import SearchItem, SearchItemTask, SearchResult

from loggat.app.util.painter import painterSaveRestore
from loggat.app.util.paths import iconPath


class Columns(int, Enum):
    tagName = 0
    logLevel = auto()
    logMessage = auto()

class LazyHighlightingState(int, Enum):
    pending = auto()
    running = auto()
    done = auto()


@dataclass
class HighlightingData:
    state: LazyHighlightingState
    items: List[SearchResult]


class CustomStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        if element == QStyle.PE_FrameFocusRect:
            # Do not draw the focus frame (dots) around selected items
            return
        super().drawPrimitive(element, option, painter, widget)


class HighlightingDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initTextDocument()
        self.rules = None
        self._background_selected = QColor("#DCDBFF")
        self._background_normal = QColor("#F2F2FF")

    def setHighlightingRules(self, rules: HighlightingRules):
        self.rules = rules

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
        data = HighlightingData(
            state=LazyHighlightingState.done,
            items=results,
        )

        model = index.model()
        model.setData(index, data, Qt.UserRole)
        model.dataChanged.emit(index, index)

    def applyHighlighting(self, index: QModelIndex):
        if index.column() != Columns.logMessage:
            return

        data: HighlightingData = index.data(Qt.UserRole)
        if data.state == LazyHighlightingState.running:
            return

        if data.state == LazyHighlightingState.done:
            self.highlightKeywords(data.items)
            return

        items = []
        for name, pattern in self.rules.iter():
            items.append(SearchItem(name, pattern))

        data.state = LazyHighlightingState.running
        task = SearchItemTask(index.data(), items)
        task.signals.finished.connect(lambda results: self.searchDone(index, results))
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

            if viewItem.state & QStyle.State_Selected:
                if index.column() in [Columns.logLevel, Columns.tagName]:
                    fmt = QTextCharFormat()
                    fmt.setFontWeight(QFont.DemiBold)
                    self.highlightAllText(fmt)

            model = index.model()
            newIndex = model.index(
                index.row(), Columns.logLevel
            )  # Example: Get data from row 1, column 1
            data = model.data(newIndex, role=Qt.DisplayRole)

            if data == "S":
                color = QColor("#CECECE")
                color.setAlphaF(0.4)
            elif data == "F":
                color = QColor("#FF2635")
                color.setAlphaF(0.4)
            elif data == "E":
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
            else:  # V
                color = QColor("orange")
                color.setAlphaF(0.4)

            painter.fillRect(viewItem.rect, color)

            self.adjustCellText(painter, viewItem)
            self.drawCell(painter)

    def highlightKeywords(self, items: List[SearchResult]):
        n = self.doc.characterCount() - 2
        for item in items:
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

class MyTableView(QTableView):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

    def setHighlightingRules(self, rules: HighlightingRules):
        self.rules = rules

    def keyPressEvent(self, event: QKeyEvent):

        def isEnterPressed():
            return event.key() in [Qt.Key_Enter, Qt.Key_Return]

        def isCtrlEnterPressed():
            return isEnterPressed() and  event.modifiers() == Qt.ControlModifier

        if isCtrlEnterPressed():
            index: QModelIndex = self.selectionModel().currentIndex()
            if index.isValid():
                model = index.model()
                if isinstance(model, CustomSortProxyModel):
                    self.doubleClicked.emit(index)

        elif isEnterPressed():
            index: QModelIndex = self.selectionModel().currentIndex()
            if index.isValid():
                model = index.model()
                if isinstance(model, CustomSortProxyModel):
                    index = model.mapToSource(index)

                proxyModel: CustomSortProxyModel = self.model()
                model: QStandardItemModel = proxyModel.sourceModel()
                tagName = model.item(index.row(), Columns.tagName).text()
                logLevel = model.item(index.row(), Columns.logLevel).text()
                logMessage = model.item(index.row(), Columns.logMessage).text()
                data: HighlightingData = model.item(index.row(), Columns.logMessage).data(Qt.UserRole)
                viewPane = LogMessageViewPane(self)
                viewPane.setLogLevel(logLevel)
                viewPane.setLogMessage(logMessage)
                viewPane.setTag(tagName)

                if logLevel == "S":
                    color = QColor("#CECECE")
                    color.setAlphaF(0.4)
                elif logLevel == "F":
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
                else:  # V
                    color = QColor("orange")
                    color.setAlphaF(0.4)

                viewPane.setItemBackgroundColor(color)
                viewPane.applyHighlighting(self.rules, data.items)
                viewPane.exec_()
        else:
            super().keyPressEvent(event)



class LogMessagesPane(QWidget):

    """Displays log messages"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.initHighlighting()

    def initHighlighting(self):
        self._delegate = HighlightingDelegate(self._tableView)
        self._tableView.setItemDelegate(self._delegate)

    def setHighlightingRules(self, rules: HighlightingRules):
        self._tableView.setHighlightingRules(rules)
        self._delegate.setHighlightingRules(rules)

    def initUserInterface(self):
        labels = ["Tag", "Log level", "Message"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        proxyModel = CustomSortProxyModel()
        proxyModel.setSourceModel(dataModel)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        tableView = MyTableView(self)
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
        self._searchField.addAction(QIcon(iconPath("search")), QLineEdit.LeadingPosition)

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
        cnt = self._dataModel.rowCount()
        self._dataModel.removeRows(0, cnt)

    def appendRow(self, logLevel, tagName, logMessage):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        itemLogLevel = QStandardItem(logLevel)
        itemLogLevel.setFlags(flags)

        itemTagName = QStandardItem(tagName)
        itemTagName.setFlags(flags)

        data = HighlightingData(
            state=LazyHighlightingState.pending,
            items=[],
        )

        itemLogMessage = QStandardItem(logMessage)
        itemLogMessage.setData(data, Qt.UserRole)
        itemLogMessage.setFlags(flags)

        row = [itemTagName, itemLogLevel, itemLogMessage]
        self._dataModel.appendRow(row)

    def onDoubleClicked(self, index: QModelIndex):
        if self._proxyModel.filteringEnabled:
            index2 = self._proxyModel.mapToSource(index)
            self.enableDisableFilter()

            self._tableView.scrollToBottom()
            index = self._proxyModel.index(index2.row(), 0)
            self._tableView.scrollTo(index, QTableView.PositionAtCenter)
