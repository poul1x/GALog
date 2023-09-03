from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.syntax_highlight import SearchItemTask, SearchResult

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initTextDocument()
        self._items = []

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

    def applyHighlighting(self, index: QModelIndex, viewItem: QStyleOptionViewItem):
        if index.column() == Columns.tagName:
            self.highlightTag(index.data())
        if index.column() == Columns.logLevel:
            self.highlightLogLevel(index.data())
        else:
            pass

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
        self.applyHighlighting(index, viewItem)
        viewItem.text = ""

        style = self.getStyle(viewItem)
        style.drawControl(QStyle.CE_ItemViewItem, viewItem, painter)

        if index.column() == 1:
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
        self, painter: QPainter, viewItem: QStyleOptionViewItem, index: QModelIndex
    ):
        with painterSaveRestore(painter) as p:
            self._paint(p, viewItem, index)

    def highlightLogLevel(self, logLevel: str):
        logLevel = logLevel.upper()
        charFormat = QTextCharFormat()

        if logLevel == "I":
            charFormat.setForeground(QColor("#DCDCDC"))
            charFormat.setBackground(QColor("#2E2D2D"))
        elif logLevel == "E":
            charFormat.setForeground(QColor("#FF5454"))
            charFormat.setBackground(QColor("#EBEBEB"))
        else:
            charFormat.setForeground(QColor("#6352B9"))
            charFormat.setBackground(QColor("#EBEBEB"))

        self.highlightAllText(charFormat)

    def highlightTag(self, tag: str):
        tag = tag.lower()
        charFormat = QTextCharFormat()

        if tag == "dalvikvm":
            charFormat.setForeground(QColor("#DCDCDC"))
            charFormat.setBackground(QColor("#2E2D2D"))
        elif tag == "Process":
            charFormat.setForeground(QColor("#FF5454"))
            charFormat.setBackground(QColor("#EBEBEB"))
        else:
            charFormat.setForeground(QColor("#6352B9"))
            charFormat.setBackground(QColor("#EBEBEB"))

        # 'Process' 'ActivityManager' 'ActivityThread' 'AndroidRuntime' 'jdwp' 'StrictMode' 'DEBUG'
        return charFormat

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
        cursor = self.cursorSelect(keyword.posBegin, keyword.posEnd)
        cursor.mergeCharFormat(charFormat)


class LogMessagesPane(QWidget):

    """Displays log messages"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.initHighlightning()

    def initHighlightning(self):
        self._delegate = HighlightingDelegate(self)
        self._tableView.setItemDelegate(self._delegate)
        # self._tableView.setItemDelegateForColumn(Columns.logMessage, self._delegate)
        self._threadPool = QThreadPool()
        self._threadPool.setMaxThreadCount(3)

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

        # Set the selection background color
        selection_palette = QPalette()
        # # selection_palette.setColor(QPalette.Text, Qt.yellow) # +
        # selection_palette.setColor(QPalette.Base, Qt.magenta) # base = background table
        # selection_palette.setColor(QPalette.HighlightedText, Qt.red) # + foreground on select
        selection_palette.setColor(
            QPalette.Highlight, Qt.blue
        )  # + background on select
        # selection_palette.setColor(QPalette.HighlightedText, Qt.blue)
        tableView.setPalette(selection_palette)
        # tableView.setStyleSheet("QTableView { background-color: green; }")

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

        document = QTextDocument()
        itemLogMessage.setData(QVariant(document), Qt.UserRole)

        # task = SearchItemTask(logMessage)
        # nextRow = self._dataModel.rowCount()
        # self._threadPool.start(task)
        # task.signals.finished.connect(lambda results: self.highlightReady(nextRow, results))

        row = [itemLogLevel, itemTagName, itemLogMessage]
        self._dataModel.appendRow(row)

    def myslot(self):
        pass

    def highlightReady(self, row: int, results: List[SearchResult]):
        self._delegate.updateResults(row, results)
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
