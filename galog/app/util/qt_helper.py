from typing import Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QStandardItem
from PyQt5.QtCore import (
    QRect,
    QSize,
    Qt,
    QSortFilterProxyModel,
    QModelIndex,
    QItemSelectionModel,
)
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QApplication,
    QComboBox,
)
from galog.app.components.capture_pane.body import SearchInputCanActivate
from galog.app.util.table_view import TableView

from PyQt5.QtCore import QRect, QSize, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget

from enum import Enum, auto


def selectRowByIndex(tableView: QTableView, index: QModelIndex):
    selectionModel = tableView.selectionModel()
    selectionModel.clear()

    tableView.setCurrentIndex(index)
    selectionModel.select(index, QItemSelectionModel.Select)
    tableView.scrollTo(index, QTableView.PositionAtCenter)
