from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QProxyStyle,
    QStyle,
    QWidget,
    QToolButton,
)

from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.paths import iconFile

class SearchInput(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isArrowPressed():
            self.focusNextChild()
            nextChild = QApplication.focusWidget()
            QApplication.postEvent(nextChild, QKeyEvent(event))
        else:
            super().keyPressEvent(event)

    def initUserInterface(self):
        self.setPlaceholderText("Search")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)
        self.findChild(QToolButton).setIcon(QIcon(iconFile("close")))
        self.setClearButtonEnabled(True)

