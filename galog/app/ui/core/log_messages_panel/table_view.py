from typing import Optional

from PyQt5.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QKeyEvent, QPainter, QResizeEvent
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget

from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.helpers.painter import painterSaveRestore
from galog.app.ui.base.table_view import TableView as BaseTableView

from .data_model import Column, DataModel
from .delegate import StyledItemDelegate
from .data_model import FnFilterModel, RegExpFilterModel
from .quick_nav import QuickNavigationFrame


class VerticalHeader(QHeaderView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Vertical, parent)
        self._font = QFont()
        self._font.setPixelSize(19)
        self._font.setFamily("Roboto")
        self._font.setWeight(QFont.Bold)

    def _selectedRows(self):
        return [index.row() for index in self.selectionModel().selectedRows()]

    def paintSection(self, _painter: QPainter, rect: QRect, index: int):
        align = Qt.AlignCenter
        lightColor = QColor("#FFFFFF")
        darkColor = QColor("#464646")

        with painterSaveRestore(_painter) as painter:
            if index in self._selectedRows():
                painter.fillRect(rect, darkColor)
                painter.setPen(lightColor)
            else:
                painter.fillRect(rect, lightColor)
                painter.setPen(darkColor)

            painter.setFont(self._font)
            painter.drawText(rect, align, str(index + 1))

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self._font)
        rowNum = self.model().rowCount()
        return QSize(fm.width(str(rowNum)) + 5, 0)


class TableView(BaseTableView):
    rowGoToOrigin = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.initCustomDelegate()
        self.initUserInterface()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlEnterPressed():
            self.rowGoToOrigin.emit()
        else:
            super().keyPressEvent(event)

    def initCustomDelegate(self):
        self.delegate = StyledItemDelegate(self)
        self.setItemDelegate(self.delegate)

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.regExpFilterModel = RegExpFilterModel()
        self.regExpFilterModel.setFilteringColumn(Column.logMessage.value)

        self.fnFilterModel = FnFilterModel()
        self.fnFilterModel.setFilteringColumn(Column.tagName.value)

        self.fnFilterModel.setSourceModel(self.dataModel)
        self.regExpFilterModel.setSourceModel(self.fnFilterModel)
        self.setModel(self.regExpFilterModel)

        self.setCornerButtonEnabled(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableView.ExtendedSelection)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)

        hHeader = self.horizontalHeader()
        hHeader.setSectionResizeMode(Column.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setColumnWidth(Column.logLevel, 10)
        self.setColumnWidth(Column.tagName, 200)

        font = self.delegate.font()
        height = QFontMetrics(font).height()
        height += 5  # vertical padding

        vHeader = VerticalHeader(self)
        self.setVerticalHeader(vHeader)
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setMinimumSectionSize(height)
        vHeader.setDefaultSectionSize(height)
        vHeader.setVisible(False)

        self.quickNavFrame = QuickNavigationFrame(self)
        self.quickNavFrame.setMarginTop(self.horizontalHeader().height() + 10)
        self.quickNavFrame.setMarginBottom(10)
        self.quickNavFrame.setMarginRight(30)
        self.quickNavFrame.setFixedWidth(120)
        self.quickNavFrame.updateGeometry()
        self.quickNavFrame.hideChildren()

        self.quickNavFrame.upArrowButton.clicked.connect(self._upArrowButtonClicked)  # fmt: skip
        self.quickNavFrame.downArrowButton.clicked.connect(self._downArrowButtonClicked)  # fmt: skip

    def _upArrowButtonClicked(self):
        rowCount = self.regExpFilterModel.rowCount()
        if rowCount > 0:
            self.scrollToTop()
            self.selectRow(0)

    def _downArrowButtonClicked(self):
        rowCount = self.regExpFilterModel.rowCount()
        if rowCount > 0:
            self.scrollToBottom()
            self.selectRow(rowCount - 1)

    def resizeEvent(self, e: QResizeEvent) -> None:
        self.quickNavFrame.updateGeometry()
        return super().resizeEvent(e)
