from typing import Optional
from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QSortFilterProxyModel, Qt, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView, QVBoxLayout, QWidget, QComboBox, QPushButton, QHBoxLayout

from galog.app.ui.base.widget import BaseWidget
from galog.app.ui.reusable import SearchInput
from galog.app.ui.base.list_view import BaseListView

from enum import Enum,auto

class FilterField(int, Enum):
    Message = 0
    Tag = auto()
    LogLevel = auto()


class QuickFilterBar(BaseWidget):
    arrowUpPressed = pyqtSignal()
    arrowDownPressed = pyqtSignal()
    startSearch = pyqtSignal(FilterField, str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initUserInterface()
        self._initFocusPolicy()
        self._initUserInputHandlers()
        self.reset()

    def _initFocusPolicy(self):
        self.startSearchButton.setFocusPolicy(Qt.NoFocus)
        self.searchByDropdown.setFocusPolicy(Qt.NoFocus)
        self.searchInput.setFocusPolicy(Qt.StrongFocus)

    def _initUserInputHandlers(self):
        # self.startSearchButton.clicked.connect()
        self.searchInput.arrowUpPressed.connect(lambda: self.arrowUpPressed.emit())
        self.searchInput.arrowDownPressed.connect(lambda: self.arrowDownPressed.emit())

    def _initUserInterface(self):
        self.searchInput = SearchInput(self)
        self.searchInput.setPlaceholderText("Search message")
        self.setFocusProxy(self.searchInput)

        self.searchByDropdown = QComboBox(self)
        self.searchByDropdown.addItem("Message")
        self.searchByDropdown.addItem("Tag")
        self.searchByDropdown.addItem("Log Level")

        self.startSearchButton = QPushButton(self)
        self.startSearchButton.setText("Search")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.searchInput, 1)
        layout.addWidget(self.searchByDropdown)
        layout.addWidget(self.startSearchButton)
        self.setLayout(layout)

    def _startSearch(self):
        filterField = FilterField(self.searchByDropdown.currentIndex())
        self.startSearch.emit(filterField, self.searchInput.text())

    def reset(self):
        self.searchByDropdown.setCurrentIndex(FilterField.Message.value)
        self.searchInput.clear()

