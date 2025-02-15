from enum import Enum, auto

from PyQt5.QtWidgets import QCheckBox

from .message_box import MessageBox


class StopCaptureDialogResult(int, Enum):
    AcceptedDetachApp = 0
    AcceptedKillApp = auto()
    Rejected = auto()


class StopCaptureDialog(MessageBox):

    AcceptedDetachApp = StopCaptureDialogResult.AcceptedDetachApp
    AcceptedKillApp = StopCaptureDialogResult.AcceptedKillApp
    Rejected = StopCaptureDialogResult.Rejected

    def __init__(self):
        super().__init__()
        self.setHeaderText("Stop capture")
        self.setWindowTitle("Stop capture")
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
                return StopCaptureDialog.AcceptedKillApp
            else:
                return StopCaptureDialog.AcceptedDetachApp
        else:
            return StopCaptureDialog.Rejected
