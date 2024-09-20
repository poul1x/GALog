from typing import List, Optional

from PySide6.QtCore import QStringListModel, Qt, Signal
from PySide6.QtWidgets import QCompleter, QWidget

from galog.app.util.paths import styleSheetFile

from ..search_input import SearchInput
from .delegate import CompleterDelegate


class SearchInputAutoComplete(SearchInput):
    completionAccepted = Signal(str)

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

        with open(styleSheetFile("completer")) as f:
            styleSheet = f.read()

        # s = r"border: 1px solid black; border-left: 2px solid black; border-right: 2px solid black;"
        self._completer.popup().window().setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
        self._completer.popup().setStyleSheet(styleSheet)

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
