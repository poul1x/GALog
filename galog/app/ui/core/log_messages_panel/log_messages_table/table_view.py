from typing import Optional

from PyQt5.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QKeyEvent, QMouseEvent, QPainter, QResizeEvent
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget
from galog.app.hrules.hrules import HRulesStorage

from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.helpers.painter import painterSaveRestore

from .data_model import Column, DataModel
from .log_line_delegate import LogLineDelegate
from .navigation_frame import NavigationFrame

from galog.app.ui.base.table_view import TableView


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


class TableView(TableView):

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() in [Qt.XButton1, Qt.XButton2]:
            event.ignore()
            return

        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        print(event.key())
        super().keyPressEvent(event)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.initLogLineDelegate()
        self.initUserInterface()

    def initLogLineDelegate(self):
        self._delegate = LogLineDelegate(self)
        self.setItemDelegate(self._delegate)

    def initUserInterface(self):
        self.setCornerButtonEnabled(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableView.ExtendedSelection)
        self.setTabKeyNavigation(False)
        self.setShowGrid(False)

        font = self._delegate.font()
        height = QFontMetrics(font).height()
        height += 5  # vertical padding

        vHeader = VerticalHeader(self)
        self.setVerticalHeader(vHeader)
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setMinimumSectionSize(height)
        vHeader.setDefaultSectionSize(height)
        vHeader.setVisible(False)


    # def resizeEvent(self, e: QResizeEvent) -> None:
    #     self.quickNavFrame.updateGeometry()
    #     return super().resizeEvent(e)

    def setHighlightingRules(self, hrules: HRulesStorage):
        self._delegate.setHighlightingRules(hrules)

    def setHighlightingEnabled(self, enabled: bool):
        self._delegate.setHighlightingEnabled(enabled)
