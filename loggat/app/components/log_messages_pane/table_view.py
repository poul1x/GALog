from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.util.hotkeys import HotkeyHelper

from .data_model import Columns
from .filter_model import FilterModel
from .delegate import StyledItemDelegate


class TableView(QTableView):
    toggleMessageFilter = pyqtSignal()

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


    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEscapePressed():
            self.toggleMessageFilter.emit()
        else:
            super().keyPressEvent(event)
