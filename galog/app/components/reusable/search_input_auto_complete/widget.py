from typing import List, Optional

from PyQt5.QtCore import Qt, QStringListModel, pyqtSignal
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtWidgets import (
    QWidget,
    QCompleter,
)

from ..search_input import SearchInput
from .delegate import CompleterDelegate


class SearchInputAutoComplete(SearchInput):
    completionAccepted = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        self._completing = False
        super().__init__(parent)

    def initUserInterface(self):
        super().initUserInterface()
        self._dataModel = QStringListModel(self)
        self._completer = QCompleter()
        self._completer.setModel(self._dataModel)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setWidget(self)
        self._completer.activated.connect(self.handleCompletion)

        s = r"border: 1px solid black; border-left: 2px solid black; border-right: 2px solid black;"
        self._completer.popup().window().setWindowFlag(Qt.NoDropShadowWindowHint, True)
        self._completer.popup().setStyleSheet(s)

        delegate = CompleterDelegate(self)
        self._completer.popup().setItemDelegate(delegate)
        self.textChanged.connect(self.handleTextChanged)

    def handleTextChanged(self, text: str):
        if not self._completing:
            found = False
            prefix = text.rpartition(",")[-1]
            if len(prefix) > 0:
                self._completer.setCompletionPrefix(prefix)
                if self._completer.currentRow() >= 0:
                    found = True
            if found:
                self._completer.complete()
            else:
                self._completer.popup().hide()

    def handleCompletion(self, text: str):
        if not self._completing:
            self._completing = True
            prefix = self._completer.completionPrefix()
            finalText = self.text()[: -len(prefix)] + text
            self.completionAccepted.emit(finalText)
            self._completing = False

    def setCompletionStrings(self, strings: List[str]):
        self._dataModel.setStringList(strings)
