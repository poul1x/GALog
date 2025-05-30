from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QLineEdit, QToolButton, QWidget

from galog.app.ui.helpers.hotkeys import HotkeyHelper
from galog.app.paths import iconFile


class SearchInput(QLineEdit):
    arrowUpPressed = pyqtSignal()
    arrowDownPressed = pyqtSignal()
    escapePressed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.XButton1:
            self.escapePressed.emit()
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isArrowUpPressed():
            self.arrowUpPressed.emit()
        elif helper.isArrowDownPressed():
            self.arrowDownPressed.emit()
        elif helper.isEscapePressed():
            self.escapePressed.emit()
        else:
            super().keyPressEvent(event)

    def initUserInterface(self):
        self.setPlaceholderText("Search")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)

        self.setClearButtonEnabled(True)
        self.findChildren(QToolButton)[1].setIcon(QIcon(iconFile("close")))
