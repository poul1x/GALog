from enum import Enum, auto
from typing import Optional
from PyQt5.QtWidgets import QWidget

from .message_box import MessageBox


class RestartCaptureDialogResult(int, Enum):
    AcceptedRestart = 0
    AcceptedRestartDebug = auto()
    Rejected = auto()


class RestartCaptureDialog(MessageBox):

    AcceptedRestart = RestartCaptureDialogResult.AcceptedRestart
    AcceptedRestartDebug = RestartCaptureDialogResult.AcceptedRestartDebug
    Rejected = RestartCaptureDialogResult.Rejected

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setHeaderText("Restart capture")
        self.setWindowTitle("Restart capture")
        self.setBodyText("Restart the capture? The app will be restarted and all captured log messages will be erased") # fmt: skip
        self.btnIdYes = self.addButton("Yes")
        self.btnIdNo = self.addButton("No")
        self.setDefaultButton(self.btnIdYes)

    def exec_(self) -> int:
        btnId = super().exec_()
        if btnId == self.btnIdYes:
            return RestartCaptureDialog.AcceptedRestart
        else:
            return RestartCaptureDialog.Rejected
