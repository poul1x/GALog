from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.syntax_highlight import SearchItemTask, SearchResult

from loggat.app.util.painter import takePainter


class Columns(int, Enum):
    logLevel = 0
    tagName = 1
    logMessage = 2


class HighlightingDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument(self)
        # Create a QFont with the desired font size
        font = QFont()
        font.setPointSize(10)  # Set the font size to 12 points
        self.doc.setDefaultFont(font)


        self._filters = []

    def paint(self, painter, option, index):
        painter.save()
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)


        fm = QFontMetrics(self.doc.defaultFont())
        elidedText = fm.elidedText(options.text, Qt.ElideRight, option.rect.width())
        self.doc.setPlainText(elidedText)

        self.default_highlight()
        self.apply_highlight()
        options.text = ""
        # style = QApplication.style() if options.widget is None \
        #     else options.widget.style()

        style = QApplication.style()
        # style = options.widget.style()
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        # Create a custom QTextOption
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignCenter)

        # Set text options on the painter
        # painter.setTextOption(text_option)

        # Customize other rendering properties if needed
        painter.setPen(Qt.blue)  # Set text color to blue
        painter.fillRect(option.rect, Qt.yellow)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        # ctx.palette.setColor(QPalette.Text, option.palette.color(
        #     QPalette.Active, QPalette.HighlightedText))

        # ctx.palette.setColor(QPalette.Text, option.palette.color(
        #     QPalette.Active, QPalette.Text))

        # if options.state & QStyle.State_Selected:
        #     ctx.palette.setColor(QPalette.Text, Qt.blue)
        #     ctx.palette.setColor(QPalette.Highlight, Qt.green) # + background on select
        #     option.palette.setColor(QPalette.Highlight, Qt.green) # + background on select
        #     options.palette.setColor(QPalette.Highlight, Qt.magenta) # + background on select
        #     options.palette.setColor(QPalette.Background, Qt.magenta) # + background on select
        # else:
        #     ctx.palette.setColor(QPalette.Text, Qt.red)

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)

        if index.column() != 0:
            textRect.adjust(4, 0, 0, 4)

        the_constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - the_constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)

        painter.restore()

        # super().paint(painter, option, index)

    def default_highlight(self):
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
