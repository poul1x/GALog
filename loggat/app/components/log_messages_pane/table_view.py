from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.util.hotkeys import HotkeyHelper

from .data_model import Columns
from .filter_model import FilterModel
from .delegate import StyledItemDelegate


class TableView(QTableView):
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
        if helper.isCtrlEnterPressed():
            index: QModelIndex = self.selectionModel().currentIndex()
            if index.isValid():
                model = index.model()
                if isinstance(model, FilterModel):
                    self.doubleClicked.emit(index)

        # elif helper.isEnterPressed():
        #     index: QModelIndex = self.selectionModel().currentIndex()
        #     if index.isValid():
        #         model = index.model()
        #         if isinstance(model, FilterModel):
        #             index = model.mapToSource(index)

        #         proxyModel: FilterModel = self.model()
        #         model: QStandardItemModel = proxyModel.sourceModel()
        #         tagName = model.item(index.row(), Columns.tagName).text()
        #         logLevel = model.item(index.row(), Columns.logLevel).text()
        #         logMessage = model.item(index.row(), Columns.logMessage).text()
        #         data: HighlightingData = model.item(
        #             index.row(), Columns.logMessage
        #         ).data(Qt.UserRole)
        #         viewPane = LogMessageViewPane(self)
        #         viewPane.setLogLevel(logLevel)
        #         viewPane.setLogMessage(logMessage)
        #         viewPane.setTag(tagName)

        #         if logLevel == "S":
        #             color = QColor("#CECECE")
        #             color.setAlphaF(0.4)
        #         elif logLevel == "F":
        #             color = QColor("#FF2635")
        #             color.setAlphaF(0.4)
        #         elif logLevel == "E":
        #             color = QColor("#FF2635")
        #             color.setAlphaF(0.4)
        #         elif logLevel == "I":
        #             color = QColor("#C7CFFF")
        #         elif logLevel == "W":
        #             color = QColor("#FFBC00")
        #             color.setAlphaF(0.5)
        #         elif logLevel == "D":
        #             color = QColor("green")
        #             color.setAlphaF(0.4)
        #         else:  # V
        #             color = QColor("orange")
        #             color.setAlphaF(0.4)

        #         viewPane.setItemBackgroundColor(color)
        #         viewPane.applyHighlighting(self.rules, data.items)
        #         viewPane.exec_()
        else:
            super().keyPressEvent(event)
