from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import QApplication, QLineEdit, QToolButton, QWidget

from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.paths import iconFile


class SearchInput(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.initUserInterface()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isArrowUpDownPressed():
            self.focusNextChild()
            nextChild = QApplication.focusWidget()
            QApplication.postEvent(nextChild, QKeyEvent(event))
        else:
            super().keyPressEvent(event)

    def initUserInterface(self):
        self.setPlaceholderText("Search")
        self.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)

        self.setClearButtonEnabled(True)
        self.findChildren(QToolButton)[1].setIcon(QIcon(iconFile("close")))
