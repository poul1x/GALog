from enum import Enum, auto
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QWidget

from galog.app.ui.base.widget import Widget
from galog.app.ui.reusable.search_input import SearchInput


class FilterField(int, Enum):
    Message = 0
    Tag = auto()
    LogLevel = auto()


class QuickFilterBar(Widget):
    escapePressed = pyqtSignal()
    arrowUpPressed = pyqtSignal()
    arrowDownPressed = pyqtSignal()
    startSearch = pyqtSignal(FilterField, str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._initUserInterface()
        self._initFocusPolicy()
        self._initUserInputHandlers()
        self.reset()
        self.hide()

    def _initFocusPolicy(self):
        self._startSearchButton.setFocusPolicy(Qt.NoFocus)
        self._searchByDropdown.setFocusPolicy(Qt.NoFocus)
        self._searchInput.setFocusPolicy(Qt.StrongFocus)

    def _initUserInputHandlers(self):
        self._searchInput.arrowUpPressed.connect(lambda: self.arrowUpPressed.emit())
        self._searchInput.arrowDownPressed.connect(lambda: self.arrowDownPressed.emit())
        self._searchInput.escapePressed.connect(lambda: self.escapePressed.emit())
        self._searchInput.returnPressed.connect(self._startSearch)
        self._startSearchButton.clicked.connect(self._startSearch)

    def _initUserInterface(self):
        self._searchInput = SearchInput(self)
        self._searchInput.setPlaceholderText("Search message")
        self.setFocusProxy(self._searchInput)

        self._searchByDropdown = QComboBox(self)
        self._searchByDropdown.addItem("Message")
        self._searchByDropdown.addItem("Tag")
        self._searchByDropdown.addItem("Log Level")

        self._startSearchButton = QPushButton(self)
        self._startSearchButton.setText("Search")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._searchInput, 1)
        layout.addWidget(self._searchByDropdown)
        layout.addWidget(self._startSearchButton)
        self.setLayout(layout)

    def _startSearch(self):
        filterField = FilterField(self._searchByDropdown.currentIndex())
        self.startSearch.emit(filterField, self._searchInput.text())

    def reset(self):
        self._searchByDropdown.setCurrentIndex(FilterField.Message.value)
        self._searchInput.clear()
