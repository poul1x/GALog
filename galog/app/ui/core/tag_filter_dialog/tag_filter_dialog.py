import os
from typing import IO
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
)
from galog.app.app_state import AppState, TagFilteringConfig, TagFilteringMode

from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from galog.app.ui.base.dialog import BaseDialog
from galog.app.ui.actions.read_file import ReadFileAction
from galog.app.ui.actions.write_file import WriteFileAction
from galog.app.ui.helpers.file_filter import FileFilter, FileFilterBuilder
from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.ui.quick_dialogs.loading_dialog import LoadingDialog

from .bottom_button_bar import BottomButtonBar
from .control_button_bar import ControlButtonBar
from .filter_type_switch import FilterTypeSwitch
from .filtered_tags_list import FilteredTagsList
from .tag_name_input import TagNameInput


class TagFilterDialog(BaseDialog):
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
        self.filteredTagsList.selectionChanged.connect(self._tagListSelectionChanged)
        self.tagNameInput.textChanged.connect(self._tagInputStateChanged)
        self.tagNameInput.completionAccepted.connect(self._addTag)
        self.tagNameInput.returnPressed.connect(self._btnAddTagClicked)
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

        self.setTabOrder(self.filteredTagsList.listView, self.tagNameInput)
        self.setTabOrder(self.tagNameInput, self.filteredTagsList.listView)
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
            if not msgBoxPrompt(caption, body):
                return

        self.accept()

    def _addTag(self, tag: str):
        if self.filteredTagsList.hasTag(tag):
            msgBrief = "Tag exists"
            msgVerbose = "Tag has been already added to this filter"
            msgBoxErr(msgBrief, msgVerbose)
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
        removedRows = self.filteredTagsList.removeSelectedTags()
        assert len(removedRows) > 0

        rowToSelect = sorted(removedRows)[0]
        if not self.filteredTagsList.selectTagByRow(rowToSelect):
            if not self.filteredTagsList.selectTagByRow(rowToSelect - 1):
                # Empty tag list -> focus on input widget
                self.tagNameInput.setFocus()

        self._updateRemoveAllTagsButtonState()
        self._updateRemoveTagButtonState()

    def _removeAllTags(self):
        self.filteredTagsList.removeAllTags()
        self._updateControlButtonBarState()
        self.tagNameInput.setFocus()

    def _askSaveTagFilePath(self):
        return QFileDialog.getSaveFileName(
            caption="Save Tag List File",
            directory=self._appState.lastUsedDirPath,
            filter=FileFilterBuilder.textFile(),
        )[0]

    def _askOpenTagFilePath(self):
        return QFileDialog.getOpenFileName(
            caption="Open Tag List File",
            directory=self._appState.lastUsedDirPath,
            filter=FileFilterBuilder.textFile(),
        )[0]

    def _saveLastSelectedDir(self, filePath: str):
        self._appState.lastUsedDirPath = os.path.dirname(filePath)

    def _readTagList(self, f: IO[str]):
        tags = list(filter(lambda s: bool(s), f.read().split()))
        self.filteredTagsList.setTags(tags)

    def _writeTagList(self, f: IO[str]):
        f.write("\n".join(self.filteredTagsList.toStringList()))

    def _loadTagsFromFile(self):
        filePath = self._askOpenTagFilePath()
        if not filePath:
            return

        self._saveLastSelectedDir(filePath)
        action = ReadFileAction(filePath)
        action.readTextData(self._readTagList)
        self._updateControlButtonBarState()

    def _saveTagsToFile(self):
        filePath = self._askSaveTagFilePath()
        if not filePath:
            return

        self._saveLastSelectedDir(filePath)
        action = WriteFileAction(filePath)
        action.writeTextData(self._writeTagList)
        self._updateControlButtonBarState()
