from enum import Enum, auto

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget


class RunAppAction(int, Enum):
    StartApp = auto()
    StartAppDebug = auto()
    DoNotStartApp = auto()


class ButtonBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("CapturePaneButtonBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layoutLeft = QHBoxLayout()
        layoutLeft.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layoutRight = QHBoxLayout()
        layoutRight.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.selectButton = QPushButton("Select")
        self.selectButton.setEnabled(False)
        self.selectButton.setProperty("name", "select")
        self.selectButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layoutLeft.addWidget(self.selectButton)

        self.fromApkButton = QPushButton("From APK")
        self.fromApkButton.setProperty("name", "fromAPK")
        self.fromApkButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layoutLeft.addWidget(self.fromApkButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setProperty("name", "cancel")
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layoutRight.addWidget(self.cancelButton)

        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)
