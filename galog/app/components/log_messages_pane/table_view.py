from typing import Optional

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QKeyEvent, QPainter
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget

from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.painter import painterSaveRestore
from galog.app.util.table_view import TableView as BaseTableView

from .data_model import Column, DataModel
from .delegate import StyledItemDelegate
from .filter_model import FnFilterModel, RegExpFilterModel


class VerticalHeader(QHeaderView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Orientation.Vertical, parent)
        self._font = QFont()
        self._font.setPixelSize(20)
        self._font.setFamily("Arial")
        self._font.setWeight(QFont.Weight.Bold)

    def _selectedRows(self):
        return [index.row() for index in self.selectionModel().selectedRows()]

    def paintSection(self, _painter: QPainter, rect: QRect, index: int):
        align = Qt.AlignmentFlag.AlignCenter
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
        return QSize(fm.horizontalAdvance(str(rowNum)) + 5, 0)


class TableView(BaseTableView):
    rowGoToOrigin = Signal()

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
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)

        hHeader = self.horizontalHeader()
        hHeader.setSectionResizeMode(Column.logMessage, QHeaderView.ResizeMode.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setColumnWidth(Column.logLevel, 10)
        self.setColumnWidth(Column.tagName, 200)

        font = self.delegate.font()
        height = QFontMetrics(font).height()
        height += 5  # vertical padding

        vHeader = VerticalHeader(self)
        self.setVerticalHeader(vHeader)
        vHeader.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        vHeader.setMinimumSectionSize(height)
        vHeader.setDefaultSectionSize(height)
        vHeader.setVisible(False)
