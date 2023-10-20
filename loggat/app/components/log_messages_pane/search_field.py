from typing import Optional
from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeyEvent, QIcon
from loggat.app.util.hotkeys import HotkeyHelper
from loggat.app.util.paths import iconFile


class SearchField(QLineEdit):
    toggleMessageFilter = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        self.setPlaceholderText("Search log message")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isEscapePressed():
            self.toggleMessageFilter.emit()
        else:
            # Allow default behavior for other key presses
            super().keyPressEvent(event)
