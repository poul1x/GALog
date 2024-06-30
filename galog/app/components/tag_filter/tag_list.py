from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from galog.app.util.list_view import ListView

from galog.app.util.paths import iconFile


class TagList(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout(self)
        self.addTagInput = QComboBox(self)
        self.tagList = ListView(self)
        self.tagList.setEditTriggers(QListView.NoEditTriggers)

        self.dataModel = QStandardItemModel(self)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)
        self.tagList.setModel(self.filterModel)
        vBoxLayout.addWidget(self.tagList)





        self.setLayout(vBoxLayout)