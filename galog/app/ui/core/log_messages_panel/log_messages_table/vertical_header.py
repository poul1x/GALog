from typing import Optional

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QHeaderView, QWidget

from galog.app.settings import readSettings
from galog.app.ui.helpers.painter import painterSaveRestore


class VerticalHeader(QHeaderView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Vertical, parent)
        self._settings = readSettings()
        self._setDefaultFont()

    def _setDefaultFont(self):
        family = self._settings.fonts.standard.family
        size = self._settings.fonts.standard.size
        self._font = QFont(family, size, QFont.Bold)

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
