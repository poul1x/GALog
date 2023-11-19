from enum import Enum, auto

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QWidget

from galog.app.util.paths import iconFile


class RunAppAction(int, Enum):
    StartApp = auto()
    StartAppDebug = auto()
    DoNotStartApp = auto()


class CapturePaneHeader(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("CapturePaneHeader")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()
        layoutLeft = QHBoxLayout()
        layoutLeft.setAlignment(Qt.AlignLeft)
        layoutRight = QHBoxLayout()
        layoutRight.setAlignment(Qt.AlignRight)

        self.deviceLabel = QLabel(self)
        self.deviceLabel.setText("Device:")
        layoutLeft.addWidget(self.deviceLabel)

        self.deviceDropDown = QComboBox(self)
        layoutLeft.addWidget(self.deviceDropDown)

        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload packages")
        layoutRight.addWidget(self.reloadButton)

        self.actionLabel = QLabel(self)
        self.actionLabel.setText("Action:")
        layoutLeft.addWidget(self.actionLabel)

        self.actionDropDown = QComboBox(self)
        self.actionDropDown.addItem("Start app", RunAppAction.StartApp)
        self.actionDropDown.addItem("Start app (debug)", RunAppAction.StartAppDebug)
        self.actionDropDown.addItem("Don't start app", RunAppAction.DoNotStartApp)
        layoutLeft.addWidget(self.actionDropDown)

        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)
