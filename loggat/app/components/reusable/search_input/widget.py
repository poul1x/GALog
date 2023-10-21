from typing import List, Optional
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from loggat.app.util.paths import iconFile


class SearchInputStyleAddon(QProxyStyle):
    def standardIcon(self, standardIcon, option=None, widget=None):
        if standardIcon == QStyle.SP_LineEditClearButton:
            return QIcon(iconFile("clear"))
        return super().standardIcon(standardIcon, option, widget)


class SearchInput(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self.setPlaceholderText("Search")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)
        self.setStyle(SearchInputStyleAddon(self.style()))
        self.setClearButtonEnabled(True)
