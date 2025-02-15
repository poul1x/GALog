from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeyEvent

from galog.app.ui.helpers.hotkeys import HotkeyHelper

from ..search_input import SearchInput


class SearchInputCanActivate(SearchInput):
    #
    # Use this signal to give an ability to user
    # to select package directly from search input with <Enter> key press.
    # Without this feature user has to press <Tab> first, only then press <Enter>
    #
    activate = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        helper = HotkeyHelper(event)
        if helper.isEnterPressed():
            self.activate.emit()

        return super().keyPressEvent(event)
