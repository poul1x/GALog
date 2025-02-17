from typing import List, Optional

from PyQt5.QtCore import QStringListModel, Qt, pyqtSignal
from PyQt5.QtWidgets import QCompleter, QWidget

from galog.app.paths import styleSheetFile

from ..search_input_can_activate import SearchInputCanActivate
from .delegate import CompleterDelegate


class SearchInputAutoComplete(SearchInputCanActivate):
    completionAccepted = pyqtSignal(str)
    POPUP_STYLESHEET: Optional[str] = None

    def __init__(self, parent: Optional[QWidget] = None):
        self._completing = False
        self._loadStyleSheet()
        super().__init__(parent)

    @staticmethod
    def _loadStyleSheet():
        if not SearchInputAutoComplete.POPUP_STYLESHEET:
            with open(styleSheetFile("completer")) as f:
                SearchInputAutoComplete.POPUP_STYLESHEET = f.read()

    def initUserInterface(self):
        super().initUserInterface()
        self._dataModel = QStringListModel(self)
        self._completer = QCompleter()
        self._completer.setModel(self._dataModel)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setWidget(self)
        self._completer.activated.connect(self.handleCompletion)

        self._completer.popup().window().setWindowFlag(Qt.NoDropShadowWindowHint, True)
        self._completer.popup().setStyleSheet(SearchInputAutoComplete.POPUP_STYLESHEET)

        delegate = CompleterDelegate(self)
        self._completer.popup().setItemDelegate(delegate)
        self.textEdited.connect(self.handleTextEdited)

    def handleTextEdited(self, text: str):
        if self._completing:
            return

        found = False
        if len(text) > 0:
            self._completer.setCompletionPrefix(text)
            if self._completer.currentRow() >= 0:
                found = True

        if found:
            self._completer.complete()
        else:
            self._completer.popup().hide()

    def handleCompletion(self, text: str):
        if self._completing:
            return

        self._completing = True
        prefix = self._completer.completionPrefix()
        finalText = self.text()[: -len(prefix)] + text
        self.completionAccepted.emit(finalText)
        self._completing = False

    def setCompletionStrings(self, strings: List[str]):
        self._dataModel.setStringList(strings)
