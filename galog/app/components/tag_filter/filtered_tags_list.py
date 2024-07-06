from typing import List
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPalette, QFont
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListView,
    QAbstractItemView,
    QCompleter,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from galog.app.util.list_view import ListView


class CompleterDelegate(QStyledItemDelegate):
    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super(CompleterDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignLeft
        font = QFont("Arial")
        font.setPixelSize(20)
        option.font = font
        if option.state & QStyle.State_MouseOver:
            option.backgroundBrush = QColor("#464646")
            option.palette.setBrush(QPalette.Text, QColor("#ffffff"))
        else:
            option.backgroundBrush = QColor("#ffffff")
            option.palette.setBrush(QPalette.Text, QColor("#464646"))


class FilteredTagsList(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setAlignment(Qt.AlignTop)
        vBoxLayout.setContentsMargins(10, 0, 10, 0)
        vBoxLayout.setSpacing(0)

        self.tagNameInput = QLineEdit(self)
        self.tagNameInput.setPlaceholderText("Enter tag to add")

        self.tagListView = ListView(self)
        self.tagListView.setEditTriggers(QListView.NoEditTriggers)
        self.tagListView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.dataModel = QStandardItemModel(self)
        self.tagListView.setModel(self.dataModel)
        vBoxLayout.addWidget(self.tagNameInput)
        vBoxLayout.addWidget(self.tagListView)
        self.setLayout(vBoxLayout)
        tags = ["System", "galog", "qweerwrt", "qwasds", "Cpature Reciever", "OkHTTP"]
        self.addManyTags(tags)

        self.completer = QCompleter()
        self.completer.setModel(self.dataModel)
        self.completer.set
        # self.completer.setCompletionMode(QCompleter.InlineCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setWidget(self.tagNameInput)
        self.completer.activated.connect(self.handleCompletion)
        delegate = CompleterDelegate(self.tagNameInput)
        self.completer.popup().setItemDelegate(delegate)
        self.tagNameInput.textChanged.connect(self.handleTextChanged)
        self._completing = False

    def _selectedRows(self):
        selectionModel = self.tagListView.selectionModel()
        return [index.row() for index in selectionModel.selectedRows()]

    def addTag(self, tag: str):
        self.dataModel.appendRow(QStandardItem(tag))

    def addManyTags(self, tags: List[str]):
        for tag in tags:
            self.dataModel.appendRow(QStandardItem(tag))

    def hasSelectedTags(self):
        return bool(self._selectedRows())

    def removeSelectedTags(self):
        for row in self._selectedRows():
            self.dataModel.removeRow(row)

    def removeAllTags(self):
        self.dataModel.clear()

    def handleTextChanged(self, text: str):
        if not self._completing:
            found = False
            prefix = text.rpartition(",")[-1]
            if len(prefix) > 1:
                self.completer.setCompletionPrefix(prefix)
                if self.completer.currentRow() >= 0:
                    found = True
            if found:
                self.completer.complete()
            else:
                self.completer.popup().hide()

    def handleCompletion(self, text):
        if not self._completing:
            self._completing = True
            prefix = self.completer.completionPrefix()
            self.tagNameInput.setText(self.tagNameInput.text()[: -len(prefix)] + text)
            self._completing = False
