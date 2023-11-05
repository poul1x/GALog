from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListView,
    QComboBox,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtGui import (
    QKeyEvent,
    QIcon,
    QStandardItemModel,
)

from galog.app.components.reusable.search_input import SearchInput
from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.paths import iconFile

from enum import Enum, auto

class RunAppAction(int, Enum):
    StartApp = auto()
    StartAppDebug = auto()
    DoNotStartApp = auto()

class CapturePaneBody(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("CapturePaneBody")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()


    def initUserInterface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.packagesList = QListView(self)
        self.packagesList.setEditTriggers(QListView.NoEditTriggers)

        self.dataModel = QStandardItemModel(self)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)
        self.packagesList.setModel(self.filterModel)
        layout.addWidget(self.packagesList)

        self.searchInput = SearchInput(self)
        self.searchInput.textChanged.connect(self.filterModel.setFilterFixedString)
        self.searchInput.setPlaceholderText("Search package")
        layout.addWidget(self.searchInput)

        self.setLayout(layout)


