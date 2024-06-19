from enum import Enum, auto

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QWidget, QLineEdit


IP_REGEXP = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
PORT_REGEXP = r"^(?![7-9]\d\d\d\d)(?!6[6-9]\d\d\d)(?!65[6-9]\d\d)(?!655[4-9]\d)(?!6553[6-9])(?!0+)\d{1,5}$"

class AdbServerAddress(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("AdbServerAddress")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()

        ipAddressLabel = QLabel(self)
        ipAddressLabel.setText("ADB Server IPv4 address:")
        layout.addWidget(ipAddressLabel)

        self.ipAddressInput = QLineEdit(self)
        self.ipAddressInput.setValidator(QRegExpValidator(QRegExp(IP_REGEXP)))
        layout.addWidget(self.ipAddressInput)

        portLabel = QLabel(self)
        portLabel.setText("Port:")
        layout.addWidget(portLabel)

        self.portInput = QLineEdit(self)
        self.portInput.setValidator(QRegExpValidator(QRegExp(PORT_REGEXP)))
        layout.addWidget(self.portInput)
        self.setLayout(layout)

    def getIpAddress(self):
        return self.ipAddressInput.text()

    def getPort(self):
        return self.portInput.text()
