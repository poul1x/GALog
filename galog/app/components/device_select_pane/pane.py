from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QStandardItem, QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QApplication,
    QComboBox,
)
from galog.app.components.capture_pane.body import SearchInputCanActivate

from galog.app.components.reusable.search_input.widget import SearchInput
from galog.app.util.hotkeys import HotkeyHelper

from galog.app.util.paths import iconFile

from .adb_server_address import AdbServerAddress
from .device_table import DeviceTable
from .button_bar import ButtonBar


class DeviceSelectPane(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("DeviceSelectPane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()
        self.setGeometryAuto()

    # def keyPressEvent(self, event: QKeyEvent):
    #     helper = HotkeyHelper(event)
    #     if helper.isEscapePressed():
    #         self.toggleMessageFilter.emit()
    #     elif helper.isCtrlCPressed():
    #         self.copyRowsToClipboard.emit()
    #     else:
    #         super().keyPressEvent(event)

    def initUserInterface(self):

        hBoxLayoutTop = QHBoxLayout()
        alignLeft = Qt.AlignLeft | Qt.AlignVCenter
        alignRight = Qt.AlignRight | Qt.AlignVCenter

        self.adbServerAddress = AdbServerAddress(self)
        hBoxLayoutTop.addWidget(self.adbServerAddress, alignment=alignLeft)

        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload devices")
        hBoxLayoutTop.addWidget(self.reloadButton, alignment=alignRight)

        ############################################################
        # Layout Main
        ############################################################

        vBoxLayoutMain = QVBoxLayout()
        vBoxLayoutMain.addLayout(hBoxLayoutTop)

        self.deviceTable = DeviceTable(self)
        vBoxLayoutMain.addWidget(self.deviceTable)

        buttonBar = ButtonBar(self)
        vBoxLayoutMain.addWidget(buttonBar)

        self.setLayout(vBoxLayoutMain)

        # self.searchPane.button.setFocusPolicy(Qt.NoFocus)
        # self.searchPane.input.setFocusPolicy(Qt.NoFocus)
        # self.tableView.setFocusPolicy(Qt.StrongFocus)
        # self.tableView.setFocus()

        # self.setTabOrder(self.tableView, self.searchPane.input)
        # self.setTabOrder(self.searchPane.input, self.tableView)

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.4)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)
