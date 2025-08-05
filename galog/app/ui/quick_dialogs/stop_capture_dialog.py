from enum import Enum, auto
from typing import Optional

from PyQt5.QtWidgets import QCheckBox, QWidget

from .message_box import MessageBox


class StopCaptureDialogResult(int, Enum):
    AcceptedDetachApp = 0
    AcceptedStopApp = auto()
    Rejected = auto()


class StopCaptureDialog(MessageBox):
    AcceptedDetachApp = StopCaptureDialogResult.AcceptedDetachApp
    AcceptedStopApp = StopCaptureDialogResult.AcceptedStopApp
    Rejected = StopCaptureDialogResult.Rejected

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setHeaderText("Stop capture")
        self.setBodyText("All captured log messages will remain there")
        self.btnIdYes = self.addButton("Yes")
        self.btnIdNo = self.addButton("No")
        self.setDefaultButton(self.btnIdYes)

        checkBox = QCheckBox("Kill app process", self)
        checkBox.setChecked(True)
        self.setCheckBox(checkBox)

    def exec_(self) -> int:
        btnId = super().exec_()
        if btnId == self.btnIdYes:
            if self.checkBox().isChecked():
                return StopCaptureDialog.AcceptedStopApp
            else:
                return StopCaptureDialog.AcceptedDetachApp
        else:
            return StopCaptureDialog.Rejected
