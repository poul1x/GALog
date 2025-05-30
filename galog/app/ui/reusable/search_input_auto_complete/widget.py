from typing import List, Optional, Tuple

from PyQt5.QtGui import QFocusEvent, QValidator
from PyQt5.QtCore import QStringListModel, Qt, pyqtSignal, QObject, QEvent, QModelIndex

from PyQt5.QtWidgets import QCompleter, QWidget

from galog.app.paths import styleSheetFile

from ..search_input import SearchInput
from .delegate import CompleterDelegate


class SearchInputAutoComplete(SearchInput):
    textSubmitted = pyqtSignal(str)
    completionAccepted = pyqtSignal(str)
    POPUP_STYLESHEET: Optional[str] = None

    def __init__(self, parent: Optional[QWidget] = None):
        self._suppressReturnPressed = False
        self._completing = False
        self._loadStyleSheet()
        super().__init__(parent)

    @staticmethod
    def _loadStyleSheet():
        if not SearchInputAutoComplete.POPUP_STYLESHEET:
            with open(styleSheetFile("completer")) as f:
                SearchInputAutoComplete.POPUP_STYLESHEET = f.read()

    def _initUserInterface(self):
        super()._initUserInterface()
        self._completer = QCompleter()
        self._dataModel = QStringListModel(self)
        self._completer.setModel(self._dataModel)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setWidget(self)

        self._completer.popup().window().setWindowFlag(Qt.NoDropShadowWindowHint, True)
        self._completer.popup().setStyleSheet(SearchInputAutoComplete.POPUP_STYLESHEET)
        self._completer.popup().setItemDelegate(CompleterDelegate(self))

        self._completer.activated.connect(self._handleCompleterItemChosen)
        self._completer.highlighted[QModelIndex].connect(self._handleCompleterItemSelected)  # fmt: skip

        self.textEdited.connect(self._handleTextEdited)
        self.returnPressed.connect(self._handleReturnPressed)

    def focusInEvent(self, a0: QFocusEvent) -> None:
        self._suppressReturnPressed = False
        return super().focusInEvent(a0)

    def _handleReturnPressed(self):
        if self._suppressReturnPressed:
            return

        text = self.text()
        if text:
            self.textSubmitted.emit(text)

    def _handleCompleterItemSelected(self, index: QModelIndex):
        self._suppressReturnPressed = index.row() != -1

    def _handleTextEdited(self, text: str):
        found = False
        if len(text) > 0:
            self._completer.setCompletionPrefix(text)
            if self._completer.currentRow() != -1:
                found = True

        if found:
            self._completer.complete()
        else:
            self._completer.popup().hide()

    def _handleCompleterItemChosen(self, text: str):
        self.completionAccepted.emit(text)

    def setCompletionStrings(self, strings: List[str]):
        self._dataModel.setStringList(strings)
