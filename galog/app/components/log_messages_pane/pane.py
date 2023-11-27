from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QFont, QFontMetrics
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QPushButton, QVBoxLayout, QWidget

from galog.app.components.reusable.search_input.widget import SearchInput
from galog.app.util.hotkeys import HotkeyHelper

from .data_model import Columns, DataModel
from .filter_model import FilterModel
from .table_view import TableView


class SearchPane(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("LogMessagesSearchPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        self.input = SearchInput(self)
        self.input.setPlaceholderText("Search message")

        self.button = QPushButton(self)
        self.button.setText("Search")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.input, 1)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.hide()


class LogMessagesPane(QWidget):
    toggleMessageFilter = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("LogMessagesPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEscapePressed():
            self.toggleMessageFilter.emit()
        else:
            super().keyPressEvent(event)

    def initUserInterface(self):
        self.tableView = TableView(self)
        self.dataModel = self.tableView.dataModel
        self.filterModel = self.tableView.filterModel

        layout = QVBoxLayout()
        self.searchPane = SearchPane(self)
        layout.addWidget(self.tableView, 1)
        layout.addWidget(self.searchPane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.searchPane.button.setFocusPolicy(Qt.NoFocus)
        self.searchPane.input.setFocusPolicy(Qt.NoFocus)
        self.tableView.setFocusPolicy(Qt.StrongFocus)
        self.tableView.setFocus()

        self.setTabOrder(self.tableView, self.searchPane.input)
        self.setTabOrder(self.searchPane.input, self.tableView)
