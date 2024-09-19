from typing import Optional

from PyQt5.QtCore import QModelIndex, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QComboBox,
    QAction,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from galog.app.components.reusable.search_input.widget import SearchInput
from galog.app.util.hotkeys import HotkeyHelper

from .table_view import TableView


class SearchPane(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("LogMessagesSearchPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        self.input = SearchInput(self)
        self.input.setPlaceholderText("Search message")
        self.setFocusProxy(self.input)

        self.searchByDropdown = QComboBox(self)
        self.searchByDropdown.addItem("Message")
        self.searchByDropdown.addItem("Tag")
        self.searchByDropdown.addItem("Log Level")

        self.button = QPushButton(self)
        self.button.setText("Search")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.input, 1)
        layout.addWidget(self.searchByDropdown)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.hide()


class LogMessagesPane(QWidget):
    toggleMessageFilter = pyqtSignal()
    copyRowsToClipboard = pyqtSignal()
    cmViewMessage = pyqtSignal(QModelIndex)
    cmGoToOrigin = pyqtSignal(QModelIndex)
    cmGoBack = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("LogMessagesPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEscapePressed():
            self.toggleMessageFilter.emit()
        elif helper.isCtrlCPressed():
            self.copyRowsToClipboard.emit()
        else:
            super().keyPressEvent(event)

    def showContextMenu(self, position: QPoint):
        index = self.tableView.indexAt(position)
        if not index.isValid():
            return

        contextMenu = QMenu(self)
        actionView = QAction("View", self)
        actionOrigin = QAction("Go to origin", self)
        actionBack = QAction("Go back", self)
        actionView.triggered.connect(lambda: self.cmViewMessage.emit(index))
        actionOrigin.triggered.connect(lambda: self.cmGoToOrigin.emit(index))
        actionBack.triggered.connect(lambda: self.cmGoBack.emit())

        contextMenu.addAction(actionView)
        contextMenu.addAction(actionOrigin)
        contextMenu.addAction(actionBack)
        contextMenu.exec_(self.tableView.viewport().mapToGlobal(position))

    def initUserInterface(self):
        self.tableView = TableView(self)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)

        self.dataModel = self.tableView.dataModel
        self.regExpFilterModel = self.tableView.regExpFilterModel
        self.fnFilterModel = self.tableView.fnFilterModel

        layout = QVBoxLayout()
        self.searchPane = SearchPane(self)
        layout.addWidget(self.tableView, 1)
        layout.addWidget(self.searchPane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.searchPane.button.setFocusPolicy(Qt.NoFocus)
        self.searchPane.searchByDropdown.setFocusPolicy(Qt.NoFocus)
        self.searchPane.input.setFocusPolicy(Qt.StrongFocus)
        self.searchPane.setFocusPolicy(Qt.StrongFocus)

        self.setTabOrder(self.tableView, self.searchPane.input)
        self.setTabOrder(self.searchPane.input, self.tableView)
        self.tableView.setFocus()
