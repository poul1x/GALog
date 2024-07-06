from typing import List, Optional

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtWidgets import QApplication, QLineEdit, QProxyStyle, QStyle, QWidget, QCompleter
from ..search_input import SearchInput
from .delegate import CompleterDelegate

from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.paths import iconFile

class SearchInputStyleAddon(QProxyStyle):
    def standardIcon(self, standardIcon, option=None, widget=None):
        if standardIcon == QStyle.SP_LineEditClearButton:
            return QIcon(iconFile("clear"))
        return super().standardIcon(standardIcon, option, widget)


class SearchInputAutoComplete(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.initUserInterface2()
        self._completing = False

    def initUserInterface2(self):
        self._dataModel = QStringListModel(self)
        self._completer = QCompleter()
        self._completer.setModel(self._dataModel)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setWidget(self)
        self._completer.activated.connect(self.handleCompletion)

        delegate = CompleterDelegate(self)
        self._completer.popup().setItemDelegate(delegate)
        self.textChanged.connect(self.handleTextChanged)

        self.setPlaceholderText("Search")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)
        self.setStyle(SearchInputStyleAddon(self.style()))
        self.setClearButtonEnabled(True)


    def handleTextChanged(self, text: str):
        if not self._completing:
            found = False
            prefix = text.rpartition(",")[-1]
            if len(prefix) > 1:
                self._completer.setCompletionPrefix(prefix)
                if self._completer.currentRow() >= 0:
                    found = True
            if found:
                self._completer.complete()
            else:
                self._completer.popup().hide()

    def handleCompletion(self, text):
        if not self._completing:
            self._completing = True
            prefix = self._completer.completionPrefix()
            self.setText(self.text()[: -len(prefix)] + text)
            self._completing = False

    def setCompletionStrings(self, strings: List[str]):
        self._dataModel.setStringList(strings)
