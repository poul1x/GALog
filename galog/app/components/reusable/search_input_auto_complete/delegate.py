from typing import Optional
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QWidget,
    QStyleOptionViewItem,
    QStyle,
)

class CompleterDelegate(QStyledItemDelegate):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._font = QFont("Arial")
        self._font.setPixelSize(20)

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        option.displayAlignment = Qt.AlignLeft
        option.font = self._font

        if option.state & QStyle.State_MouseOver:
            option.backgroundBrush = QColor("#464646")
            option.palette.setBrush(QPalette.Text, QColor("#ffffff"))
        elif option.state & QStyle.State_Selected:
            option.backgroundBrush = QColor("#464646")
            option.palette.setBrush(QPalette.Text, QColor("#ffffff"))
        else:
            option.backgroundBrush = QColor("#ffffff")
            option.palette.setBrush(QPalette.Text, QColor("#464646"))

        super().initStyleOption(option, index)