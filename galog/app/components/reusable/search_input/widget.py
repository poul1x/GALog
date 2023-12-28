from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtWidgets import QLineEdit, QProxyStyle, QStyle, QWidget
from galog.app.util.hotkeys import HotkeyHelper

from galog.app.util.paths import iconFile


class SearchInputStyleAddon(QProxyStyle):
    def standardIcon(self, standardIcon, option=None, widget=None):
        if standardIcon == QStyle.SP_LineEditClearButton:
            return QIcon(iconFile("clear"))
        return super().standardIcon(standardIcon, option, widget)


class SearchInput(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isArrowPressed():
            self.focusNextPrevChild(True)
        else:
            super().keyPressEvent(event)

    def initUserInterface(self):
        self.setPlaceholderText("Search")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)
        self.setStyle(SearchInputStyleAddon(self.style()))
        self.setClearButtonEnabled(True)
