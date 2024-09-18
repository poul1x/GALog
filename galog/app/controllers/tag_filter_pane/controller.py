from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from PyQt5.QtCore import QModelIndex, Qt, QThread, QThreadPool
from PyQt5.QtGui import QGuiApplication, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QTableView

from galog.app.components.dialogs import LoadingDialog
from galog.app.components.log_messages_pane.data_model import Column
from galog.app.components.log_messages_pane.delegate import (
    HighlightingData,
    LazyHighlightingState,
)
from galog.app.components.log_messages_pane.pane import LogMessagesPane
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.components.tag_filter_pane import TagFilteringMode, TagFilterPane
from galog.app.controllers.message_view_pane.controller import (
    LogMessageViewPaneController,
)
from galog.app.controllers.open_tag_file import OpenTagFileController
from galog.app.controllers.save_tag_file import SaveTagFileController
from galog.app.device.device import AdbClient
from galog.app.highlighting import HighlightingRules
from galog.app.util.message_box import showErrorMsgBox, showErrorMsgBox2

if TYPE_CHECKING:
    from galog.app.main import MainWindow
else:
    MainWindow = object


@dataclass
class TagFilteringConfig:
    mode: TagFilteringMode
    tags: List[str]


class TagFilterPaneController:
    def __init__(self, mainWindow: MainWindow):
        self._mainWindow = mainWindow
        self._config = TagFilteringConfig(mode=TagFilteringMode.Disabled, tags=[])
        self._pane = None

    def exec_(self, tagList: List[str] = []):
        self._pane = TagFilterPane(self._mainWindow)
        self._pane.tagNameInput.setCompletionStrings(tagList)
        self._pane.controlButtonBar.addTagButton.clicked.connect(
            self._handleAddTag,
        )
        self._pane.controlButtonBar.removeTagButton.clicked.connect(
            self._handleRemoveSelectedTags
        )
        self._pane.controlButtonBar.removeAllTagsButton.clicked.connect(
            self._handleRemoveAllTags
        )
        self._pane.controlButtonBar.saveToFileButton.clicked.connect(
            self._handleSaveTagsToFile
        )
        self._pane.controlButtonBar.loadFromFileButton.clicked.connect(
            self._handleLoadTagsFromFile
        )
        self._pane.tagNameInput.completionAccepted.connect(
            self._handleAddTagCompleted,
        )
        self._pane.tagNameInput.textChanged.connect(
            self._handleInputStateChanged,
        )
        self._pane.filteredTagsList.selectionChanged.connect(
            self._handleFilteredTagsSelection
        )
        self._pane.bottomButtonBar.buttonSave.clicked.connect(
            self._handleButtonSaveClicked,
        )
        self._pane.bottomButtonBar.buttonCancel.clicked.connect(
            lambda: self._pane.reject()
        )

        self._applyFilteringConfig()

        res = self._pane.exec_()
        if res == TagFilterPane.Accepted:
            self._saveFilteringConfig()

    exec = exec_

    def _saveFilteringConfig(self):
        switch = self._pane.filterTypeSwitch
        tagList = self._pane.filteredTagsList
        self._config = TagFilteringConfig(
            mode=switch.filteringMode(),
            tags=tagList.toStringList(),
        )

    def _applyFilteringConfig(self):
        switch = self._pane.filterTypeSwitch
        tagList = self._pane.filteredTagsList
        switch.setFilteringMode(self._config.mode)
        tagList.setTags(self._config.tags)
        self._updateControlButtonBarState()

    def _handleButtonSaveClicked(self):
        self._saveFilteringConfig()
        self._pane.accept()

    def filteringConfig(self):
        return self._config

    def setFilteringConfig(self, config: TagFilteringConfig):
        self._config = config

    def _addTagInternal(self, tag: str):
        if self._pane.filteredTagsList.hasTag(tag):
            msg = "Tag already exists in this filter"
            showErrorMsgBox2(msg)
            return

        self._pane.tagNameInput.clear()
        self._pane.filteredTagsList.addTag(tag)
        self._updateControlButtonBarState()

    def _handleInputStateChanged(self):
        self._updateAddButtonState()

    def _handleAddTag(self):
        tag = self._pane.tagNameInput.text()
        self._addTagInternal(tag)

    def _handleAddTagCompleted(self, tag: str):
        self._addTagInternal(tag)

    def _updateAddButtonState(self):
        hasInput = bool(self._pane.tagNameInput.text())
        self._pane.controlButtonBar.addTagButton.setEnabled(hasInput)

    def _updateControlButtonBarState(self):
        self._updateAddButtonState()
        self._updateRemoveTagButtonState()
        self._updateRemoveAllTagsButtonState()
        self._updateSaveTagsToFileButtonState()

    def _updateSaveTagsToFileButtonState(self):
        enabled = self._pane.filteredTagsList.hasTags()
        self._pane.controlButtonBar.saveToFileButton.setEnabled(enabled)

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
        self._pane.filteredTagsList.removeSelectedTags()
        self._updateRemoveAllTagsButtonState()
        self._updateRemoveTagButtonState()

    def _handleRemoveAllTags(self):
        self._pane.filteredTagsList.removeAllTags()
        self._updateControlButtonBarState()

    def _handleSaveTagsToFile(self):
        tagsList = self._pane.filteredTagsList.toStringList()
        controller = SaveTagFileController(tagsList)
        controller.promptSaveFile()

    def _handleLoadTagsFromFile(self):
        controller = OpenTagFileController()
        result = controller.promptOpenFile()
        if not result:
            return

        self._pane.filteredTagsList.setTags(result)
        self._updateControlButtonBarState()
