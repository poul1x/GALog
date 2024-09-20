from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent


class HotkeyHelper:
    def __init__(self, event: QKeyEvent):
        self._event = event

    def isEnterPressed(self):
        return self._event.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]

    def isCtrlPressed(self):
        return self._event.modifiers() == Qt.KeyboardModifier.ControlModifier

    def isEscapePressed(self):
        return self._event.key() == Qt.Key.Key_Escape

    def isSpacePressed(self):
        return self._event.key() == Qt.Key.Key_Space

    def isArrowUpDownPressed(self):
        return self._event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down]

    def isCtrlCPressed(self):
        return self._event.key() == Qt.Key.Key_C and self.isCtrlPressed()

    def isCtrlDPressed(self):
        return self._event.key() == Qt.Key.Key_D and self.isCtrlPressed()

    def isCtrlRPressed(self):
        return self._event.key() == Qt.Key.Key_R and self.isCtrlPressed()

    def isCtrlFPressed(self):
        return self._event.key() == Qt.Key.Key_F and self.isCtrlPressed()

    def isCtrlEnterPressed(self):
        return self.isCtrlPressed() and self.isEnterPressed()
