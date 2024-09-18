from PyQt5.QtWidgets import QWidget

from galog.app.components.reusable.search_input_auto_complete import (
    SearchInputAutoComplete,
)


class TagNameInput(SearchInputAutoComplete):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setPlaceholderText("Enter tag to add")
