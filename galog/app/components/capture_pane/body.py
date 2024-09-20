from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from PySide6.QtGui import QKeyEvent, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QVBoxLayout, QWidget

from galog.app.components.reusable.search_input import SearchInput
from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.list_view import ListView


class SearchInputCanActivate(SearchInput):
    #
    # Use this signal to give an ability to user
    # to select package directly from search input with <Enter> key press.
    # Without this feature user has to press <Tab> first, only then press <Enter>
    #
    activate = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        helper = HotkeyHelper(event)
        if helper.isEnterPressed():
            self.activate.emit()

        return super().keyPressEvent(event)


class CapturePaneBody(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("CapturePaneBody")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.packagesList = ListView(self)
        self.packagesList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.dataModel = QStandardItemModel(self)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)
        self.packagesList.setModel(self.filterModel)
        layout.addWidget(self.packagesList)

        self.searchInput = SearchInputCanActivate(self)
        self.searchInput.setPlaceholderText("Search package")
        layout.addWidget(self.searchInput)

        self.setLayout(layout)
