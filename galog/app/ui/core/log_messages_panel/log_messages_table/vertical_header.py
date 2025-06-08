from typing import Callable, List, Optional

from galog.app.hrules.hrules import HRulesStorage
from galog.app.log_reader.models import LogLine
from galog.app.ui.helpers.painter import painterSaveRestore

from .navigation_frame import NavigationFrame

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal, QSortFilterProxyModel, QRect, QSize
from PyQt5.QtGui import QKeyEvent, QResizeEvent, QStandardItemModel, QFocusEvent, QMouseEvent, QGuiApplication, QFont, QPainter, QColor, QFontMetrics
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QTableView, QTableWidget
)

from galog.app.ui.reusable.search_input import SearchInput
from galog.app.ui.reusable.regexp_filter_model import RegExpFilterModel
from galog.app.ui.reusable.fn_filter_model import FnFilterModel

from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.base.widget import Widget

from .data_model import Column, DataModel
from .navigation_frame import NavigationFrame


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
