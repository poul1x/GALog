from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget

from galog.app.paths import iconFile
from galog.app.ui.base.widget import BaseWidget


class MessageBoxContentArea(BaseWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout(self)

        self.iconLabel = QLabel(self)
        self.iconLabel.setAlignment(Qt.AlignCenter)
        self.iconLabel.setObjectName("MessageBoxIconLabel")
        self.iconLabel.setContentsMargins(0, 0, 0, 0)
        self.setIcon(QIcon(iconFile("msgbox-info")))

        self.mainTextLabel = QLabel(self)
        self.mainTextLabel.setObjectName("MessageBoxMainTextLabel")
        self.mainTextLabel.setWordWrap(True)
        self.mainTextLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        hBoxLayout.addWidget(self.iconLabel)
        hBoxLayout.addWidget(self.mainTextLabel, 1)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setSpacing(0)
        self.setLayout(hBoxLayout)

    def setBodyText(self, text: str):
        self.mainTextLabel.setText(text)

    def setIcon(self, icon: QIcon):
        self.iconLabel.setPixmap(icon.pixmap(64, 64))
