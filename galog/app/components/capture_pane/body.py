from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal
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


class SearchInputCanActivate(SearchInput):
    #
    # Use this signal to give an ability to user
    # to select package directly from search input with <Enter> key press.
    # Without this feature user has to press <Tab> first, only then press <Enter>
    #
    activate = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        helper = HotkeyHelper(event)
        if helper.isEnterPressed():
            self.activate.emit()

        return super().keyPressEvent(event)


class CapturePaneBody(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("CapturePaneBody")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
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

        self.searchInput = SearchInputCanActivate(self)
        self.searchInput.setPlaceholderText("Search package")
        layout.addWidget(self.searchInput)

        self.setLayout(layout)
