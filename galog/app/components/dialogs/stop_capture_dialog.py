from enum import Enum, auto

from PySide6.QtWidgets import QCheckBox

from .message_box import MessageBox


class StopCaptureDialogResult(int, Enum):
    AcceptedDetachApp = auto()
    AcceptedKillApp = auto()
    Rejected = auto()


class StopCaptureDialog(MessageBox):
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

    def exec(self) -> int:
        btnId = super().exec()
        if btnId == self.btnIdYes:
            if self.checkBox().isChecked():
                return StopCaptureDialogResult.AcceptedKillApp
            else:
                return StopCaptureDialogResult.AcceptedDetachApp
        else:
            return StopCaptureDialogResult.Rejected
