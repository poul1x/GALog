from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from galog.app.paths import iconFile
from galog.app.ui.base.dialog import Dialog


class LogMessageViewDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.setWindowTitle("View log message")
        self.setRelativeGeometry(0.8, 0.8, 900, 600)
        self.setFixedMinSize(500, 400)
        self.moveToCenter()

    def initUserInterface(self):
        self.logLevelLabel = QLabel()
        self.logLevelLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logLevelLabel.setFixedWidth(300)
        self.logLevelLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.tagNameLabel = QLabel()
        self.tagNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tagNameLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.copyButton = QPushButton()
        self.copyButton.setIcon(QIcon(iconFile("copy")))
        self.copyButton.setText("Copy contents")
        self.copyButton.setFixedWidth(220)

        self.copyButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.copyButton.setIconSize(QSize(32, 32))

        hLeftBoxLayout = QHBoxLayout()
        hLeftBoxLayout.addWidget(self.logLevelLabel)
        hLeftBoxLayout.addWidget(self.tagNameLabel)
        hLeftBoxLayout.setAlignment(Qt.AlignLeft)

        hRightBoxLayout = QHBoxLayout()
        hRightBoxLayout.addWidget(self.copyButton)
        hRightBoxLayout.setAlignment(Qt.AlignRight)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addLayout(hLeftBoxLayout, 1)
        hBoxLayout.addLayout(hRightBoxLayout)

        self.logMsgTextBrowser = QTextBrowser()
        self.logMsgTextBrowser.setOpenExternalLinks(True)
        self.logMsgTextBrowser.setReadOnly(True)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addWidget(self.logMsgTextBrowser, 1)
        self.setLayout(vBoxLayout)
