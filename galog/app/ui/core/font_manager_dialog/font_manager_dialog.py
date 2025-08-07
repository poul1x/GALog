from typing import List
from zipfile import BadZipFile

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QKeyEvent, QFontDatabase, QFontMetrics, QFont
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from galog.app.apk_info import APK
from galog.app.device import adbClient
from galog.app.msgbox import msgBoxErr, msgBoxPrompt
from galog.app.settings.settings import readSettings, writeSettings
from galog.app.ui.actions.install_app.action import InstallAppAction
from galog.app.ui.base.dialog import Dialog
from .font_preview_pane import FontPreviewPane
from galog.app.ui.helpers.hotkeys import HotkeyHelper

from ..device_select_dialog import DeviceSelectDialog
from .button_bar import BottomButtonBar
from .fonts_list import FontList


class FontManagerDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
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

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.fontsList.searchInput.setFocus()
        else:
            super().keyPressEvent(event)

    def _initUserInputHandlers(self):
        self.fontsList.listView.rowActivated.connect(self._fontSelected)
        self.fontsList.listView.selectionModel().currentChanged.connect(self._currentFontChanged)

        self.buttonBar.selectButton.clicked.connect(self._selectButtonClicked)
        self.buttonBar.cancelButton.clicked.connect(self.reject)

        self.fontPreviewPane.fontSizeSpinBox.valueChanged.connect(self._valueChanged)

        searchInput = self.fontsList.searchInput
        searchInput.returnPressed.connect(self._fontMayBeSelected)
        searchInput.textChanged.connect(self._manageSelectButtonOnOff)
        searchInput.arrowUpPressed.connect(self._tryFocusFontsListAndGoUp)
        searchInput.arrowDownPressed.connect(self._tryFocusFontsListAndGoDown)

    def _valueChanged(self, value: int):
        font = QFont(self.fontPreviewPane.fontFamily(), value)
        height= QFontMetrics(font).height()
        self.fontPreviewPane.fontPreview.setFixedHeight(height)
        self.fontPreviewPane.setFontSize(value)

    def _manageSelectButtonOnOff(self):
        canSelect = self.fontsList.canSelectFont()
        self.buttonBar.selectButton.setEnabled(canSelect)

    def _initUserInterface(self):
        self.setWindowTitle("Font Manager")
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.fontPreviewPane = FontPreviewPane(self)
        self.fontsList = FontList(self)
        self.buttonBar = BottomButtonBar(self)

        layout.addWidget(self.fontPreviewPane)
        layout.addWidget(self.fontsList)
        layout.addWidget(self.buttonBar)
        self.setLayout(layout)

    def _initFocusPolicy(self):
        self.fontPreviewPane.fontPreview.setFocusPolicy(Qt.NoFocus)
        self.fontPreviewPane.fontSizeSpinBox.setFocusPolicy(Qt.ClickFocus)
        self.buttonBar.selectButton.setFocusPolicy(Qt.NoFocus)
        self.buttonBar.cancelButton.setFocusPolicy(Qt.NoFocus)

        self.fontsList.searchInput.setFocus()
        self.setTabOrder(self.fontsList.searchInput, self.fontsList.listView)
        self.setTabOrder(self.fontsList.listView, self.fontsList.searchInput)

    def _tryFocusFontsListAndGoUp(self):
        self.fontsList.trySetFocusAndGoUp()

    def _tryFocusFontsListAndGoDown(self):
        self.fontsList.trySetFocusAndGoDown()

    def _setFonts(self, fonts: List[str]):
        self.fontsList.clear()
        for font in fonts:
            self.fontsList.addFont(font)

    def _fontSelected(self, index: QModelIndex):
        # fontName = self.fontsList.selectedFont(index)
        # selectedAction = self.fontPreviewPane.runAppAction()
        # selectedFont = LastSelectedFont.new(fontName, selectedAction)
        # self._settings.lastSelectedFont = selectedFont
        self.accept()

    def _fontMayBeSelected(self):
        index = self.fontsList.listView.currentIndex()
        if not index.isValid():
            return

        self._fontSelected(index)

    def _selectButtonClicked(self):
        self._fontSelected(self.fontsList.listView.currentIndex())

    def _loadFonts(self):
        fontDB = QFontDatabase()
        for fontFamily in fontDB.families():
            self.fontsList.addFont(fontFamily)

        assert not self.fontsList.empty()
        self.fontsList.selectFirstFont()

    def setFontFamily(self, fontName: str):
        if self.fontsList.hasFont(fontName):
            self.fontsList.selectFontByName(fontName)
            self.fontPreviewPane.setFontFamily(fontName)

    def setFontSize(self, fontSize: str):
        self.fontPreviewPane.setFontSize(fontSize)

    def fontFamily(self):
        return self.fontsList.selectedFont()

    def fontSize(self):
        return self.fontPreviewPane.fontSize()

    def _currentFontChanged(self, current: QModelIndex, previous: QModelIndex):
        if not current.isValid():
            return

        data = self.fontsList.filterModel.data(current)
        self.fontPreviewPane.setFontFamily(data)