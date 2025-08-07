from enum import Enum, auto
from typing import Callable, List
from zipfile import BadZipFile

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QKeyEvent, QFontDatabase, QFontMetrics, QFont
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from galog.app.apk_info import APK
from galog.app.device import adbClient
from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from galog.app.settings.models import FontSettings
from galog.app.settings.settings import readSettings, writeSettings
from galog.app.ui.actions.install_app.action import InstallAppAction
from galog.app.ui.base.dialog import Dialog
from .font_preview_pane import FontPreviewPane
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from ..device_select_dialog import DeviceSelectDialog
from .button_bar import BottomButtonBar
from .fonts_list import FontList


class FontManagerDialog(Dialog):
    def __init__(self, parent: QWidget, objectName: str):
        super().__init__(parent, objectName)
        self._settings = readSettings()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setRelativeGeometry(0.8, 0.6, 800, 600)
        self.setFixedMaxSize(800, 600)
        self.setFixedMinSize(600, 400)
        self.moveToCenter()
        self._initUserInterface()
        self._initUserInputHandlers()
        self._initFocusPolicy()
        self._loadFonts()
        self._manageSelectButtonOnOff()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.fontList.searchInput.setFocus()
        else:
            super().keyPressEvent(event)

    def _initUserInputHandlers(self):
        self.fontList.listView.rowActivated.connect(self._fontSelected)
        self.fontList.currentFontChanged.connect(self._currentFontChanged)

        self.buttonBar.selectButton.clicked.connect(self._selectButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

        searchInput = self.fontList.searchInput
        searchInput.returnPressed.connect(self._fontMayBeSelected)
        searchInput.textChanged.connect(self._manageSelectButtonOnOff)
        searchInput.arrowUpPressed.connect(self._tryFocusFontsListAndGoUp)
        searchInput.arrowDownPressed.connect(self._tryFocusFontsListAndGoDown)

    def _manageSelectButtonOnOff(self):
        canSelect = self.fontList.canSelectFont()
        self.buttonBar.selectButton.setEnabled(canSelect)

    def _initUserInterface(self):
        self.setWindowTitle("Font Manager")
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.fontPreviewPane = FontPreviewPane(self)
        self.fontList = FontList(self)
        self.buttonBar = BottomButtonBar(self)

        layout.addWidget(self.fontPreviewPane)
        layout.addWidget(self.fontList)
        layout.addWidget(self.buttonBar)
        self.setLayout(layout)

    def _initFocusPolicy(self):
        self.fontPreviewPane.fontPreviewLabel.setFocusPolicy(Qt.NoFocus)
        self.fontPreviewPane.fontSizeSpinBox.setFocusPolicy(Qt.ClickFocus)
        self.buttonBar.selectButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.NoFocus)

        self.fontList.searchInput.setFocus()
        self.setTabOrder(self.fontList.searchInput, self.fontList.listView)
        self.setTabOrder(self.fontList.listView, self.fontList.searchInput)

    def _tryFocusFontsListAndGoUp(self):
        self.fontList.trySetFocusAndGoUp()

    def _tryFocusFontsListAndGoDown(self):
        self.fontList.trySetFocusAndGoDown()

    def _writeFontSettings(self, fontSettings: FontSettings):
        raise NotImplementedError()

    def _fontSelected(self, index: QModelIndex):
        fontFamily = self.fontPreviewPane.targetFontFamily()
        fontSize = self.fontPreviewPane.targetFontSize()
        selectedFont = FontSettings.new(fontFamily, fontSize)
        self._writeFontSettings(selectedFont)
        writeSettings(self._settings)
        self.accept()

    def _fontMayBeSelected(self):
        index = self.fontList.listView.currentIndex()
        if not index.isValid():
            return

        self._fontSelected(index)

    def _selectButtonClicked(self):
        self._fontSelected(self.fontList.listView.currentIndex())

    def _loadFonts(self):
        self._setFonts(
            self._filterFonts(
                QFontDatabase().families(),
            ),
        )

        if not self.fontList.empty():
            self.fontList.selectFirstFont()

    def _filterFonts(self, fonts: List[str]) -> List[str]:
        raise NotImplementedError()

    def _setFonts(self, fonts: List[str]):
        self.fontList.clear()
        for font in fonts:
            self.fontList.addFont(font)

    def setTargetFontFamily(self, fontName: str):
        if self.fontList.hasFont(fontName):
            self.fontList.selectFontByName(fontName)
            self.fontPreviewPane.setTargetFontFamily(fontName)

    def setTargetFontSize(self, fontSize: str):
        self.fontPreviewPane.setTargetFontSize(fontSize)

    def fontFamily(self):
        return self.fontPreviewPane.targetFontFamily()

    def fontSize(self):
        return self.fontPreviewPane.targetFontSize()

    def _currentFontChanged(self, fontFamily: str):
        self.fontPreviewPane.setTargetFontFamily(fontFamily)

    def setPreviewText(self, text: str):
        self.fontPreviewPane.setPreviewText(text)