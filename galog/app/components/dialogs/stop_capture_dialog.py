from enum import Enum, auto

from PyQt5.QtWidgets import QCheckBox
from .message_box import MessageBox


class StopCaptureDialogResult(int, Enum):
    AcceptedDetachApp = auto()
    AcceptedKillApp = auto()
    Rejected = auto()


class StopCaptureDialog(MessageBox):
    def __init__(self):
        super().__init__()
        self.setText("Stop capture")
        self.setWindowTitle("Stop capture")
        self.setInformativeText("All captured log messages will remain there")
        self.setStandardButtons(MessageBox.Yes | MessageBox.No)
        self.setDefaultButton(MessageBox.Yes)

        checkBox = QCheckBox("Kill app process", self)
        checkBox.setChecked(True)
        self.setCheckBox(checkBox)

    def exec_(self) -> int:
        result = super().exec_()
        if result == MessageBox.Yes:
            if self.checkBox().isChecked():
                return StopCaptureDialogResult.AcceptedKillApp
            else:
                return StopCaptureDialogResult.AcceptedDetachApp
        else:
            return StopCaptureDialogResult.Rejected
