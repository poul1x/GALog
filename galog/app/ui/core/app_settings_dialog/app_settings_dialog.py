from enum import Enum, auto
from typing import Callable, List
from zipfile import BadZipFile

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QKeyEvent, QFontDatabase, QFontMetrics, QFont
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QWidget, QScrollArea, QSizePolicy

from galog.app.apk_info import APK
from galog.app.device import adbClient
from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from galog.app.settings.models import FontSettings
from galog.app.settings import (
    readSettings,
    writeSettings,
    SettingsChangeNotifier,
    ChangedEntry,
    AppSettings,
)
from galog.app.settings import reloadSettings
from galog.app.ui.actions.install_app.action import InstallAppAction
from galog.app.ui.base.dialog import Dialog
from galog.app.ui.base.widget import Widget
from galog.app.ui.reusable.search_input import SearchInput
from .section_search_adapter import SectionSearchAdapter
from .font_settings_pane import FontSettingsPane
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from ..device_select_dialog import DeviceSelectDialog
from .button_bar import BottomButtonBar


class SettingsWidget(Widget):
    def __init__(self, settings: AppSettings, parent: QWidget):
        super().__init__(parent)
        self._settings = settings
        self.fontSettingsPane = FontSettingsPane(self._settings, self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.fontSettingsPane)
        self.setLayout(layout)


class AppSettingsDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._entriesChanged = set()
        self._settingsCopy = readSettings().model_copy(deep=True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setRelativeGeometry(0.8, 0.6, 800, 600)
        self.setFixedMaxSize(800, 600)
        self.setFixedMinSize(600, 400)
        self.moveToCenter()
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initFocusPolicy()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.searchInput.setFocus()
        else:
            super().keyPressEvent(event)

    def _standardFontChanged(self, fontFamily: str, fontSize: int):
        fontSettings = FontSettings.new(fontFamily, fontSize)
        self._entriesChanged.add(ChangedEntry.AppFontSettingsStandard)
        self._settingsCopy.fonts.standard = fontSettings

    def _upsizedFontChanged(self, fontFamily: str, fontSize: int):
        fontSettings = FontSettings.new(fontFamily, fontSize)
        self._entriesChanged.add(ChangedEntry.AppFontSettingsUpsized)
        self._settingsCopy.fonts.upsized = fontSettings

    def _monospacedFontChanged(self, fontFamily: str, fontSize: int):
        fontSettings = FontSettings.new(fontFamily, fontSize)
        self._entriesChanged.add(ChangedEntry.AppFontSettingsMonospaced)
        self._settingsCopy.fonts.monospaced = fontSettings

    def _emojiFontChanged(self, fontFamily: str, fontSize: int):
        fontSettings = FontSettings.new(fontFamily, fontSize)
        self._entriesChanged.add(ChangedEntry.AppFontSettingsEmoji)
        self._settingsCopy.fonts.emoji = fontSettings

    def _emojiEnabledChanged(self, value: bool):
        self._entriesChanged.add(ChangedEntry.AppFontSettingsEmoji)
        self._settingsCopy.fonts.emojiEnabled = value

    def _emojiAddSpaceChanged(self, value: bool):
        self._entriesChanged.add(ChangedEntry.AppFontSettingsEmoji)
        self._settingsCopy.fonts.emojiAddSpace = value

    def _searchTextInSettings(
        self, text: str, searchAdapters: List[SectionSearchAdapter]
    ):
        hasResults = False
        for searchAdapter in searchAdapters:
            widget = searchAdapter.value()
            hasMatch = text in searchAdapter.key()
            widget.setVisible(hasMatch)
            hasResults |= hasMatch

        return hasResults

    def _searchInFontSettingsPane(self, text: str):
        fontSettingsPane = self.settingsWidget.fontSettingsPane
        hasResults = self._searchTextInSettings(text, fontSettingsPane.searchAdapters())
        fontSettingsPane.setVisible(hasResults)
        return hasResults

    def _applySectionFilter(self, text: str):
        hasResults = False
        text = text.lower()

        hasResults |= self._searchInFontSettingsPane(text)

        hasResultsVal = "true" if hasResults else "false"
        self.settingsWidget.setProperty("hasResults", hasResultsVal)
        self.settingsWidget.refreshStyleSheet()

    def _initUserInputHandlers(self):
        self.searchInput.textChanged.connect(self._applySectionFilter)
        self.buttonBar.applyButton.clicked.connect(self._applyButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

        fontSettingsPane = self.settingsWidget.fontSettingsPane
        fontSettingsPane.standardFontChanged.connect(self._standardFontChanged)
        fontSettingsPane.upsizedFontChanged.connect(self._upsizedFontChanged)
        fontSettingsPane.monospacedFontChanged.connect(self._monospacedFontChanged)
        fontSettingsPane.emojiFontChanged.connect(self._emojiFontChanged)
        fontSettingsPane.emojiEnabledChanged.connect(self._emojiEnabledChanged)
        fontSettingsPane.emojiAddSpaceChanged.connect(self._emojiAddSpaceChanged)

    def _initUserInterface(self):
        self.setWindowTitle("App Settings")
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.settingsWidget = SettingsWidget(self._settingsCopy, self.scrollArea)
        self.scrollArea.setWidget(self.settingsWidget)

        self.buttonBar = BottomButtonBar(self)
        self.searchInput = SearchInput(self)
        self.searchInput.setPlaceholderText("Search settings")

        layout.addWidget(self.scrollArea, stretch=1)
        layout.addWidget(self.searchInput)
        layout.addWidget(self.buttonBar)
        self.setLayout(layout)

    def _initFocusPolicy(self):
        self.buttonBar.applyButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.NoFocus)

    def _notifySettingsChanged(self):
        notifier = SettingsChangeNotifier()
        for entry in self._entriesChanged:
            notifier.notify(entry)

    def _applyButtonClicked(self):
        writeSettings(self._settingsCopy, reload=True)
        self._notifySettingsChanged()
        self.accept()
