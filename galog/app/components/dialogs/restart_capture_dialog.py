from enum import Enum, auto

from PyQt5.QtWidgets import QCheckBox

from .message_box import MessageBox


class RestartCaptureDialogResult(int, Enum):
    AcceptedRestart = 0
    AcceptedRestartDebug = auto()
    Rejected = auto()


class RestartCaptureDialog(MessageBox):
    def __init__(self):
        super().__init__()
        self.setHeaderText("Restart capture")
        self.setWindowTitle("Restart capture")
        self.setBodyText("Restart the capture? The app will be restarted and all captured log messages will be erased")
        self.btnIdYes = self.addButton("Yes")
        self.btnIdNo = self.addButton("No")
        self.setDefaultButton(self.btnIdYes)

    def exec_(self) -> int:
        btnId = super().exec_()
        if btnId == self.btnIdYes:
            return RestartCaptureDialogResult.AcceptedRestart
        else:
            return RestartCaptureDialogResult.Rejected
