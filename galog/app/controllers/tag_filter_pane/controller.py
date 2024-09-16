from contextlib import contextmanager
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
from galog.app.components.tag_filter_pane import TagFilterType, TagFilterPane
from galog.app.controllers.message_view_pane.controller import (
    LogMessageViewPaneController,
)
from galog.app.device.device import AdbClient
from galog.app.highlighting import HighlightingRules
from galog.app.util.message_box import showErrorMsgBox, showErrorMsgBox2

if TYPE_CHECKING:
    from galog.app.main import MainWindow
else:
    MainWindow = object


class TagFilterPaneController:
    def __init__(self, mainWindow: MainWindow):
        self._mainWindow = mainWindow
        self._tagsInclude = []
        self._tagsExclude = []
        self._tagsTmp = []

    @contextmanager
    def _execute(self):
        result = self._pane.exec_()
        yield result
        self._pane = None
        self._tagsTmp = []

    def exec_(self):
        assert not self._tagsTmp
        self._pane = TagFilterPane(self._mainWindow)
        self._pane.controlButtonBar.addTagButton.clicked.connect(self._handleAddTag)
        self._pane.controlButtonBar.removeTagButton.clicked.connect(
            self._handleRemoveSelectedTags
        )
        self._pane.controlButtonBar.removeAllTagsButton.clicked.connect(
            self._handleRemoveAllTags
        )
        self._pane.tagNameInput.completionAccepted.connect(self._handleAddTagCompleted)
        self._pane.tagNameInput.textChanged.connect(self._handleInputStateChanged)

        self._pane.filteredTagsList.selectionChanged.connect(
            self._handleFilteredTagsSelection
        )

        self._updateAddButtonState()
        self._updateRemoveTagButtonState()
        self._updateRemoveAllTagsButtonState()

        with self._execute() as result:
            if result == TagFilterPane.Accepted:
                self.saveResults()

    exec = exec_

    def saveResults(self):
        sw = self._pane.filterTypeSwitch
        if sw.filterType() == TagFilterType.Include:
            self._tagsInclude = self._tagsTmp
        else:
            self._tagsExclude = self._tagsTmp

    def tagListInclude(self):
        return self._tagsInclude

    def tagListExclude(self):
        return self._tagsExclude

    def _addTagInternal(self, tag: str):
        if tag in self._tagsTmp:
            msg = "Tag already exists in this filter"
            showErrorMsgBox2(msg)
            return

        self._pane.filteredTagsList.addTag(tag)
        self._pane.tagNameInput.clear()
        self._tagsTmp.append(tag)

    def _handleInputStateChanged(self):
        self._updateAddButtonState()

    def _handleAddTag(self):
        tag = self._pane.tagNameInput.text()
        self._addTagInternal(tag)

    def _handleAddTagCompleted(self, tag: str):
        self._addTagInternal(tag)

    def _updateAddButtonState(self):
        hasInput = len(self._pane.tagNameInput.text()) > 0
        self._pane.controlButtonBar.addTagButton.setEnabled(hasInput)

    def _updateRemoveTagButtonState(self):
        enabled = self._pane.filteredTagsList.hasSelectedTags()
        self._pane.controlButtonBar.removeTagButton.setEnabled(enabled)

    def _updateRemoveAllTagsButtonState(self):
        enabled = self._pane.filteredTagsList.hasTags()
        self._pane.controlButtonBar.removeAllTagsButton.setEnabled(enabled)

    def _handleFilteredTagsSelection(self):
        enabled = self._pane.filteredTagsList.hasSelectedTags()
        self._pane.controlButtonBar.removeTagButton.setEnabled(enabled)

    def _handleRemoveSelectedTags(self):
        tags = self._pane.filteredTagsList.removeSelectedTags()
        self._tagsTmp = list(filter(lambda t: t not in tags, self._tagsTmp))
        self._updateRemoveAllTagsButtonState()
        self._updateRemoveTagButtonState()

    def _handleRemoveAllTags(self):
        self._pane.filteredTagsList.removeAllTags()
        self._updateRemoveAllTagsButtonState()
        self._updateRemoveTagButtonState()
        self._tagsTmp = []
