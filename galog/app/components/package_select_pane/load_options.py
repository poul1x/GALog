from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QWidget

from galog.app.app_state import RunAppAction
from galog.app.util.paths import iconFile


class PackagesLoadOptions(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("PackagesLoadOptions")
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

        self.deviceSelectButton = QPushButton(self)
        layoutLeft.addWidget(self.deviceSelectButton)

        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload packages")
        layoutRight.addWidget(self.reloadButton)

        self.actionLabel = QLabel(self)
        self.actionLabel.setText("Action:")
        layoutLeft.addWidget(self.actionLabel)

        self.actionDropDown = QComboBox(self)
        self.actionDropDown.addItem("Start app", RunAppAction.StartApp)
        # self.actionDropDown.addItem("Start app (debug)", RunAppAction.StartAppDebug)
        self.actionDropDown.addItem("Don't start app", RunAppAction.DoNotStartApp)
        layoutLeft.addWidget(self.actionDropDown)

        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)

    def deviceName(self):
        return self.deviceSelectButton.text()

    def setDeviceName(self, deviceName: str):
        return self.deviceSelectButton.setText(deviceName)

    def runAppAction(self) -> RunAppAction:
        return self.actionDropDown.currentData()

    def setRunAppAction(self, action: RunAppAction):
        i = self.actionDropDown.findData(action, Qt.UserRole)
        assert i != -1, "Current action must be present in RunAppAction"
        self.actionDropDown.setCurrentIndex(i)
