from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt


class HotkeyHelper:
    def __init__(self, event: QKeyEvent) -> None:
        self._event = event

    def isEscapePressed(self):
        return self._event.key() == Qt.Key_Escape

    def isEnterPressed(self):
        return self._event.key() in [Qt.Key_Enter, Qt.Key_Return]

    def isCtrlEnterPressed(self):
        return self.isEnterPressed() and self._event.modifiers() == Qt.ControlModifier
