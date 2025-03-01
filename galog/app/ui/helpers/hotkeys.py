from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent


class HotkeyHelper:
    def __init__(self, event: QKeyEvent):
        self._event = event

    def isEnterPressed(self):
        return self._event.key() in [Qt.Key_Enter, Qt.Key_Return]

    def isCtrlPressed(self):
        return bool(self._event.modifiers() & Qt.ControlModifier)

    def isShiftPressed(self):
        return bool(self._event.modifiers() & Qt.ShiftModifier)

    def isCtrlShiftPressed(self):
        return self.isCtrlPressed() and self.isShiftPressed()

    def isEscapePressed(self):
        return self._event.key() == Qt.Key_Escape

    def isSpacePressed(self):
        return self._event.key() == Qt.Key_Space

    def isArrowUpPressed(self):
        return self._event.key() == Qt.Key_Up

    def isArrowDownPressed(self):
        return self._event.key() == Qt.Key_Down

    def isCtrlCPressed(self):
        return self._event.key() == Qt.Key_C and self.isCtrlPressed()

    def isCtrlShiftCPressed(self):
        return self._event.key() == Qt.Key_C and self.isCtrlShiftPressed()

    def isCtrlDPressed(self):
        return self._event.key() == Qt.Key_D and self.isCtrlPressed()

    def isCtrlRPressed(self):
        return self._event.key() == Qt.Key_R and self.isCtrlPressed()

    def isCtrlFPressed(self):
        return self._event.key() == Qt.Key_F and self.isCtrlPressed()

    def isCtrlOPressed(self):
        return self._event.key() == Qt.Key_O and self.isCtrlPressed()

    def isCtrlSPressed(self):
        return self._event.key() == Qt.Key_S and self.isCtrlPressed()

    def isDelPressed(self):
        return self._event.key() == Qt.Key_Delete

    def isCtrlEnterPressed(self):
        return self.isCtrlPressed() and self.isEnterPressed()
