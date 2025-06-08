from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QWidget

from galog.app.app_state import AppState, TagFilteringConfig, TagFilteringMode
from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from galog.app.ui.actions.read_tags_file import ReadTagsFileAction
from galog.app.ui.actions.write_tags_file import WriteTagsFileAction
from galog.app.ui.base.dialog import Dialog
from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.reusable.file_picker import FileExtensionFilterBuilder, FilePicker

from .bottom_button_bar import BottomButtonBar
from .control_button_bar import ControlButtonBar
from .filter_type_switch import FilterTypeSwitch
from .filtered_tags_list import FilteredTagsList
from .tag_name_input import TagNameInput


class TagFilterDialog(Dialog):
    Accepted = 1
    Rejected = 0

    def __init__(self, appState: AppState, parent: QWidget):
        super().__init__(parent)
        self._appState = appState
        self.setWindowTitle("Tag Filter")
        self.setRelativeGeometry(0.2, 0.35, 450, 400)
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initFocusPolicy()

    def setTagAutoCompletionStrings(self, tagList: List[str]):
        self.tagNameInput.setCompletionStrings(tagList)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlOPressed():
            self._loadTagsFromFile()
        elif helper.isCtrlSPressed():
            self._saveTagsToFile()
        elif helper.isDelPressed():
            self._removeSelectedTags()
        else:
            super().keyPressEvent(event)

    def _initUserInterface(self):
        self.filterTypeSwitch = FilterTypeSwitch(self)
        self.controlButtonBar = ControlButtonBar(self)
        self.tagNameInput = TagNameInput(self)
        self.filteredTagsList = FilteredTagsList(self)
        self.bottomButtonBar = BottomButtonBar(self)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(10, 0, 10, 0)
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(self.tagNameInput)
        vBoxLayout.addWidget(self.filteredTagsList)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 10, 0, 10)
        hBoxLayout.setSpacing(0)
        hBoxLayout.addLayout(vBoxLayout, stretch=1)
        hBoxLayout.addWidget(self.controlButtonBar)

        vBoxLayoutMain = QVBoxLayout()
        vBoxLayoutMain.setContentsMargins(0, 10, 0, 0)
        vBoxLayoutMain.setSpacing(0)
        vBoxLayoutMain.addWidget(self.filterTypeSwitch)
        vBoxLayoutMain.addLayout(hBoxLayout, stretch=1)
        vBoxLayoutMain.addWidget(self.bottomButtonBar)
        self.setLayout(vBoxLayoutMain)

    def exec_(self) -> int:
        self._applyFilteringConfig()
        result = super().exec_()
        if result == QDialog.Accepted:
            self._saveFilteringConfig()
            return TagFilterDialog.Accepted
        else:
            return TagFilterDialog.Rejected

    exec = exec_

    def _initUserInputHandlers(self):
        self.controlButtonBar.addTagButton.clicked.connect(self._btnAddTagClicked)
        self.controlButtonBar.removeTagButton.clicked.connect(self._removeSelectedTags)
        self.controlButtonBar.removeAllTagsButton.clicked.connect(self._removeAllTags)
        self.controlButtonBar.saveToFileButton.clicked.connect(self._saveTagsToFile)
        self.controlButtonBar.loadFromFileButton.clicked.connect(self._loadTagsFromFile)
        self.filteredTagsList.selectionChange.connect(self._tagListSelectionChanged)
        self.tagNameInput.textChanged.connect(self._tagInputStateChanged)
        self.tagNameInput.completionAccepted.connect(self._addTag)
        self.tagNameInput.textSubmitted.connect(self._addTag)
        self.tagNameInput.arrowUpPressed.connect(self._tryFocusTagsListAndGoUp)
        self.tagNameInput.arrowDownPressed.connect(self._tryFocusTagsListAndGoDown)
        self.bottomButtonBar.buttonSave.clicked.connect(self._btnSaveClicked)
        self.bottomButtonBar.buttonCancel.clicked.connect(self.reject)

    def _tryFocusTagsListAndGoUp(self):
        self.filteredTagsList.trySetFocusAndGoUp()

    def _tryFocusTagsListAndGoDown(self):
        self.filteredTagsList.trySetFocusAndGoDown()

    def _initFocusPolicy(self):
        self.filterTypeSwitch.dropdown.setFocusPolicy(Qt.NoFocus)
        self.controlButtonBar.addTagButton.setFocusPolicy(Qt.NoFocus)
        self.controlButtonBar.removeTagButton.setFocusPolicy(Qt.NoFocus)
        self.controlButtonBar.removeAllTagsButton.setFocusPolicy(Qt.NoFocus)
        self.controlButtonBar.saveToFileButton.setFocusPolicy(Qt.NoFocus)
        self.controlButtonBar.loadFromFileButton.setFocusPolicy(Qt.NoFocus)
        self.bottomButtonBar.buttonSave.setFocusPolicy(Qt.NoFocus)
        self.bottomButtonBar.buttonCancel.setFocusPolicy(Qt.NoFocus)

        self.setTabOrder(self.filteredTagsList, self.tagNameInput)
        self.setTabOrder(self.tagNameInput, self.filteredTagsList)
        self.tagNameInput.setFocus()

    def _saveFilteringConfig(self):
        switch = self.filterTypeSwitch
        tagList = self.filteredTagsList
        self._appState.tagFilteringConfig = TagFilteringConfig(
            mode=switch.filteringMode(),
            tags=tagList.toStringList(),
        )

        return switch.filteringMode() != TagFilteringMode.Disabled

    def _applyFilteringConfig(self):
        mode = self._appState.tagFilteringConfig.mode
        tags = self._appState.tagFilteringConfig.tags
        self.filterTypeSwitch.setFilteringMode(mode)
        self.filteredTagsList.setTags(tags)
        self._updateControlButtonBarState()

    def _btnSaveClicked(self):
        filteringEnabled = self._saveFilteringConfig()
        if not filteringEnabled:
            caption = "Tag filter will be disabled"
            body = "Current filtering mode is set to 'disabled'. Continue without tag filtering?"
            if not msgBoxPrompt(caption, body, self):
                return

        self.accept()

    def _addTag(self, tag: str):
        if self.filteredTagsList.hasTag(tag):
            msgBrief = "Tag exists"
            msgVerbose = "Tag has been already added to this filter"
            msgBoxErr(msgBrief, msgVerbose, self)
            return

        self.tagNameInput.clear()
        self.filteredTagsList.addTag(tag)
        self._updateControlButtonBarState()

    def _tagInputStateChanged(self):
        self._updateAddButtonState()

    def _btnAddTagClicked(self):
        tag = self.tagNameInput.text()
        if tag:
            self._addTag(tag)

    def _updateAddButtonState(self):
        hasInput = bool(self.tagNameInput.text())
        self.controlButtonBar.addTagButton.setEnabled(hasInput)

    def _updateControlButtonBarState(self):
        self._updateAddButtonState()
        self._updateRemoveTagButtonState()
        self._updateRemoveAllTagsButtonState()
        self._updateSaveTagsToFileButtonState()

    def _updateSaveTagsToFileButtonState(self):
        enabled = self.filteredTagsList.hasTags()
        self.controlButtonBar.saveToFileButton.setEnabled(enabled)

    def _updateRemoveTagButtonState(self):
        enabled = self.filteredTagsList.hasSelectedTags()
        self.controlButtonBar.removeTagButton.setEnabled(enabled)

    def _updateRemoveAllTagsButtonState(self):
        enabled = self.filteredTagsList.hasTags()
        self.controlButtonBar.removeAllTagsButton.setEnabled(enabled)

    def _tagListSelectionChanged(self):
        enabled = self.filteredTagsList.hasSelectedTags()
        self.controlButtonBar.removeTagButton.setEnabled(enabled)

    def _removeSelectedTags(self):
        #
        # Get count of rows, which will be removed
        # If no rows removed, then exit
        #

        selectedRows = self.filteredTagsList.selectedRows()
        if not selectedRows:
            return

        #
        # Get the next row number
        # If we are going to remove the last row,
        # decrease the next row number by one
        #

        rowToSelect = self.filteredTagsList.selectedRows()[-1] + 1
        if rowToSelect == self.filteredTagsList.rowCount():
            rowToSelect -= 1

        #
        # Remove selected rows.
        # Our row number will be decreased by count of removed rows
        #

        removedRows = self.filteredTagsList.removeSelectedTags()
        rowToSelect -= len(removedRows)

        #
        # If tag list has at least one item, then make selection
        # Otherwise, move focus to the search input
        #

        if self.filteredTagsList.hasItems():
            self.filteredTagsList.selectRow(rowToSelect)
        else:
            self.tagNameInput.setFocus()

        #
        # Finally, Update button states
        #

        self._updateRemoveAllTagsButtonState()
        self._updateRemoveTagButtonState()

    def _removeAllTags(self):
        self.filteredTagsList.removeAllTags()
        self._updateControlButtonBarState()
        self.tagNameInput.setFocus()

    def _saveLastSelectedDir(self, filePicker: FilePicker):
        if filePicker.hasSelectedDirectory():
            self._appState.lastUsedDirPath = filePicker.selectedDirectory()

    def _loadTagsFromFile(self):
        filePicker = FilePicker(
            caption="Load tag list from file",
            directory=self._appState.lastUsedDirPath,
            extensionFilter=FileExtensionFilterBuilder.textFile(),
        )

        filePath = filePicker.askOpenFileRead()
        if not filePath:
            return

        self._saveLastSelectedDir(filePicker)
        action = ReadTagsFileAction(filePath, self)
        action.setLoadingDialogText("Loading tag list from file")
        tags = action.readTagsFile()

        if tags is not None:
            self.filteredTagsList.setTags(tags)

        self._updateControlButtonBarState()

    def _saveTagsToFile(self):
        filePicker = FilePicker(
            caption="Save tag list to file",
            directory=self._appState.lastUsedDirPath,
            extensionFilter=FileExtensionFilterBuilder.textFile(),
        )

        filePath = filePicker.askOpenFileWrite()
        if not filePath:
            return

        self._saveLastSelectedDir(filePicker)
        action = WriteTagsFileAction(filePath, self)
        action.setLoadingDialogText("Saving tag list to file")
        action.writeTagsFile(self.filteredTagsList.toStringList())
        self._updateControlButtonBarState()
