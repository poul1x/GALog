from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent


class HotkeyHelper:
    def __init__(self, event: QKeyEvent):
        self._event = event

    def isEnterPressed(self):
        return self._event.key() in [Qt.Key_Enter, Qt.Key_Return]

    def isCtrlPressed(self):
        return self._event.modifiers() == Qt.ControlModifier

    def isEscapePressed(self):
        return self._event.key() == Qt.Key_Escape

    def isSpacePressed(self):
        return self._event.key() == Qt.Key_Space

    def isArrowUpDownPressed(self):
        return self._event.key() in [Qt.Key_Up, Qt.Key_Down]

    def isCtrlCPressed(self):
        return self._event.key() == Qt.Key_C and self.isCtrlPressed()

    def isCtrlDPressed(self):
        return self._event.key() == Qt.Key_D and self.isCtrlPressed()

    def isCtrlRPressed(self):
        return self._event.key() == Qt.Key_R and self.isCtrlPressed()

    def isCtrlFPressed(self):
        return self._event.key() == Qt.Key_F and self.isCtrlPressed()

    def isCtrlEnterPressed(self):
        return self.isCtrlPressed() and self.isEnterPressed()
