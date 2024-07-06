from typing import TYPE_CHECKING, List

from PyQt5.QtCore import QModelIndex, Qt, QThread, QThreadPool
from PyQt5.QtGui import QGuiApplication, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QTableView

from galog.app.components.dialogs import LoadingDialog
from galog.app.components.log_messages_pane.data_model import Columns
from galog.app.components.log_messages_pane.delegate import (
    HighlightingData,
    LazyHighlightingState,
)
from galog.app.components.log_messages_pane.pane import LogMessagesPane
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.components.tag_filter.pane import TagFilterPane
from galog.app.controllers.message_view_pane.controller import (
    LogMessageViewPaneController,
)
from galog.app.device.device import AdbClient
from galog.app.highlighting import HighlightingRules
from galog.app.util.message_box import showErrorMsgBox

if TYPE_CHECKING:
    from galog.app.main import MainWindow
else:
    MainWindow = object


class LogMessagesPaneController:

    def __init__(self, mainWindow: MainWindow):
        self._mainWindow = mainWindow
        self.tagsInclude = []
        self.tagsExclude = []
        self.tagsTmp = []

    def exec_(self):
        self._pane = TagFilterPane(self._mainWindow)
        self._pane.controlButtonBar.addTagButton.clicked.connect(self._handleAddTag)
        self._pane.filteredTagsList.tagNameInput.completionAccepted.connect(self._handleAddTagCompl)

        result = self._pane.exec_()
        if result == "save":
            self.tagsExclude = self.tagsTmp.copy()
            self.tagsInclude = self.tagsTmp.copy()

    def _handleAddTag(self):
        tag = self._pane.filteredTagsList.addTagFromInput()
        self.tagsTmp.append(tag)

    def _handleAddTagCompl(self, tag: str):
        tag = self._pane.filteredTagsList.addTagFromInput()
        self.tagsTmp.append(tag)

    def _handleRemoveTag(self):
        self._pane.filteredTagsList.addTagFromInput()
