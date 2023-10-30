from typing import Optional
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from enum import Enum, auto

class StopCaptureDialogResult(Enum):
    AcceptedDetachApp = auto()
    AcceptedKillApp = auto()
    Rejected = auto()

class StopCaptureDialog(QDialog):

    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowCloseButtonHint

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, self._defaultFlags())
        self.initUI()

    def initUI(self):
        vBoxLayout = QVBoxLayout()
        hBoxLayoutButtons = QHBoxLayout()
        hBoxLayoutLabels = QHBoxLayout()

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        labelForIcon = QLabel()
        icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxQuestion)
        pixmap = icon.pixmap(48, 48)
        labelForIcon.setPixmap(pixmap)

        buttonYes = QPushButton("Yes", self)
        buttonYes.clicked.connect(self.accept)

        buttonNo = QPushButton("No", self)
        buttonNo.clicked.connect(self.reject)
        self.checkBox = QCheckBox("Kill app process", self)
        self.checkBox.setChecked(True)

        hBoxLayoutButtons.addWidget(buttonYes)
        hBoxLayoutButtons.addWidget(buttonNo)
        hBoxLayoutLabels.addWidget(labelForIcon)
        hBoxLayoutLabels.addWidget(self.label, 1)
        vBoxLayout.addLayout(hBoxLayoutLabels)
        vBoxLayout.addLayout(hBoxLayoutButtons)
        vBoxLayout.addWidget(self.checkBox, alignment=Qt.AlignLeft)
        self.setLayout(vBoxLayout)

    def setText(self, text: str):
        self.label.setText(text)

    def exec_(self) -> int:
        result = super().exec_()
        if result == QDialog.Accepted:
            if self.checkBox.isChecked():
                return StopCaptureDialogResult.AcceptedKillApp
            else:
                return StopCaptureDialogResult.AcceptedDetachApp
        else:
            return StopCaptureDialogResult.Rejected
