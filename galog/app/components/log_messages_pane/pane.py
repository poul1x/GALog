from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QHeaderView, QPushButton, QHBoxLayout, QVBoxLayout

from PyQt5.QtWidgets import QWidget
from galog.app.components.reusable.search_input.widget import SearchInput

from galog.app.util.hotkeys import HotkeyHelper

from .filter_model import FilterModel
from .data_model import DataModel, Columns
from .table_view import TableView

class LogMessagesPane(QWidget):
    toggleMessageFilter = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.setObjectName("LogMessagesPane")

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEscapePressed():
            self.toggleMessageFilter.emit()
        else:
            super().keyPressEvent(event)

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.filterModel = FilterModel()
        self.filterModel.setSourceModel(self.dataModel)

        self.tableView = TableView(self)
        self.tableView.setModel(self.filterModel)

        hHeader = self.tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        vHeader = self.tableView.verticalHeader()
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setDefaultSectionSize(vHeader.minimumSectionSize())
        vHeader.setVisible(False)

        self.searchInput = SearchInput(self)
        self.searchInput.setPlaceholderText("Search message")

        self.searchButton = QPushButton(self)
        self.searchButton.setText("Search")

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.searchInput)
        hLayout.addWidget(self.searchButton)
        self.searchButton.hide()
        self.searchInput.hide()

        vLayout = QVBoxLayout()
        vLayout.addWidget(self.tableView)
        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)

        self.searchButton.setFocusPolicy(Qt.NoFocus)
        self.searchInput.setFocusPolicy(Qt.NoFocus)
        self.tableView.setFocusPolicy(Qt.StrongFocus)
        self.tableView.setFocus()

        self.setTabOrder(self.tableView, self.searchInput)
        self.setTabOrder(self.searchInput, self.tableView)

