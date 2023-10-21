from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PyQt5.QtWidgets import QWidget


from .delegate import HighlightingData, LazyHighlightingState
from .filter_model import FilterModel
from .data_model import DataModel, Columns
from .table_view import TableView
from .search_field import SearchField


class LogMessagesPane(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self.dataModel = DataModel()
        self.filterModel = FilterModel()
        self.filterModel.setSourceModel(self.dataModel)

        self.tableView = TableView(self)
        self.tableView.setModel(self.filterModel)

        hHeader = self.tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.logMessage, QHeaderView.Stretch)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = self.tableView.verticalHeader()
        vHeader.setSectionResizeMode(QHeaderView.Fixed)
        vHeader.setDefaultSectionSize(vHeader.minimumSectionSize())
        vHeader.setVisible(False)

        self.searchField = SearchField(self)
        self.searchButton = QPushButton(self)
        self.searchButton.setText("Search")

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.searchField)
        hLayout.addWidget(self.searchButton)
        self.searchButton.hide()
        self.searchField.hide()

        vLayout = QVBoxLayout()
        vLayout.addWidget(self.tableView)
        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)
