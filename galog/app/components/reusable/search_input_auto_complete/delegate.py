from typing import Optional

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QColor, QFont, QPainter, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)


class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._font = QFont("Arial")
        self._font.setPixelSize(20)

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
