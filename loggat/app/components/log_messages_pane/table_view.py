from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QTableView, QWidget, QAbstractItemView
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.util.hotkeys import HotkeyHelper

from .data_model import Columns
from .delegate import StyledItemDelegate


class TableView(QTableView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.delegate = StyledItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.initUserInterface()

    def initUserInterface(self):
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setColumnWidth(Columns.logLevel, 20)
        self.setColumnWidth(Columns.tagName, 200)
        self.setShowGrid(False)