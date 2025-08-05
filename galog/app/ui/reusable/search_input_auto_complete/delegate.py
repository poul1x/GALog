from typing import Optional

from PyQt5.QtCore import QModelIndex, QSize
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from galog.app.settings import readSettings


class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = readSettings()
        self._setDefaultFont()

    def _setDefaultFont(self):
        family = self._settings.fonts.standard.family
        size = self._settings.fonts.standard.size
        self._font = QFont(family, size)

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        self.initStyleOption(option, index)

        option.font = self._font
        if option.state & QStyle.State_MouseOver:
            option.backgroundBrush = QColor("#464646")
            option.palette.setBrush(QPalette.Text, QColor("#ffffff"))
        elif option.state & QStyle.State_Selected:
            option.backgroundBrush = QColor("#464646")
            option.palette.setBrush(QPalette.Text, QColor("#ffffff"))
        else:
            option.backgroundBrush = QColor("#ffffff")
            option.palette.setBrush(QPalette.Text, QColor("#000000"))

        # If option.state is MouseOver or Selected
        # Brush color is combined with style color (blue)
        # To avoid this, set state to 0
        option.state &= 0

        widget: QWidget = option.widget
        style = widget.style() if widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, option, painter, widget)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        fm = QFontMetrics(self._font)
        size = super().sizeHint(option, index)
        return QSize(size.width(), fm.height() + 5)
