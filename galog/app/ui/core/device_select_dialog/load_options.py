from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from galog.app.paths import iconFile

IP_REGEXP = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
PORT_REGEXP = r"^(?![7-9]\d\d\d\d)(?!6[6-9]\d\d\d)(?!65[6-9]\d\d)(?!655[4-9]\d)(?!6553[6-9])(?!0+)\d{1,5}$"


class DevicesLoadOptions(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("AdbServerSettings")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QHBoxLayout()
        alignLeft = Qt.AlignLeft | Qt.AlignVCenter
        alignRight = Qt.AlignRight | Qt.AlignVCenter

        ipAddressLabel = QLabel(self)
        ipAddressLabel.setText("ADB Server IPv4 address:")
        layout.addWidget(ipAddressLabel, alignment=alignLeft)

        self.ipAddressInput = QLineEdit(self)
        self.ipAddressInput.setValidator(QRegExpValidator(QRegExp(IP_REGEXP)))
        layout.addWidget(self.ipAddressInput, alignment=alignLeft)
        self.ipAddressInput.setEnabled(False)

        portLabel = QLabel(self)
        portLabel.setText("Port:")
        layout.addWidget(portLabel, alignment=alignLeft)

        self.portInput = QLineEdit(self)
        self.portInput.setValidator(QRegExpValidator(QRegExp(PORT_REGEXP)))
        layout.addWidget(self.portInput, alignment=alignLeft)
        self.portInput.setEnabled(False)

        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload devices")
        self.reloadButton.setProperty("name", "reload")
        layout.addStretch()
        layout.addWidget(self.reloadButton, alignment=alignRight)

        self.setLayout(layout)

    def adbIpAddr(self):
        return self.ipAddressInput.text()

    def adbPort(self):
        return self.portInput.text()

    def setAdbIpAddr(self, addr: str):
        return self.ipAddressInput.setText(addr)

    def setAdbPort(self, port: str):
        return self.portInput.setText(port)
