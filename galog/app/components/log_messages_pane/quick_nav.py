from typing import Optional

from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget

from galog.app.util.paths import iconFile


class OverlayButton(QPushButton):
    def setNormalStyleSheet(self):
        self.setStyleSheet(
            """
            QPushButton {
                border: 2px solid #999999;
                background-color: white;
                border-radius: 4px;
            }
        """
        )

    def setHoverStyleSheet(self):
        self.setStyleSheet(
            """
            QPushButton {
                border: 2px solid #444444;
                background-color: #444444;
                border-radius: 4px;
            }
            """
        )

    def enterEvent(self, a0: QEvent) -> None:
        self.setModeHover()
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.setModeNormal()
        return super().leaveEvent(a0)

    def setNormalIcon(self):
        raise NotImplementedError()

    def setHoverIcon(self):
        raise NotImplementedError()

    def setModeNormal(self):
        self.setNormalIcon()
        self.setNormalStyleSheet()

    def setModeHover(self):
        self.setHoverIcon()
        self.setHoverStyleSheet()


class UpArrowButton(OverlayButton):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self._iconNormal = QIcon(iconFile("up-home"))
        self._iconHover = QIcon(iconFile("up-home-light"))
        self.setModeNormal()

    def setNormalIcon(self):
        self.setIcon(self._iconNormal)

    def setHoverIcon(self):
        self.setIcon(self._iconHover)


class DownArrowButton(OverlayButton):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self._iconNormal = QIcon(iconFile("down-end"))
        self._iconHover = QIcon(iconFile("down-end-light"))
        self.setModeNormal()

    def setNormalIcon(self):
        self.setIcon(self._iconNormal)

    def setHoverIcon(self):
        self.setIcon(self._iconHover)


class QuickNavigationFrame(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def setMarginTop(self, marginTop: int):
        self._marginTop = marginTop

    def setMarginBottom(self, marginBottom: int):
        self._marginBottom = marginBottom

    def setMarginRight(self, marginRight: int):
        self._marginRight = marginRight

    def hideChildren(self):
        self.upArrowButton.hide()
        self.downArrowButton.hide()

    def showChildren(self):
        self.upArrowButton.show()
        self.downArrowButton.show()

    def enterEvent(self, a0: QEvent) -> None:
        self.showChildren()
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.hideChildren()
        return super().enterEvent(a0)

    def setFixedWidth(self, width: int):
        super().setFixedWidth(width)
        self.upArrowButton.setFixedHeight(width // 2)
        self.downArrowButton.setFixedHeight(width // 2)

    def initUserInterface(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        vBoxLayout = QVBoxLayout(self)

        self.upArrowButton = UpArrowButton(self)
        vBoxLayout.addWidget(self.upArrowButton)

        splitter = QWidget(self)
        splitter.setAttribute(Qt.WA_TranslucentBackground)
        vBoxLayout.addWidget(splitter, 1)

        self.downArrowButton = DownArrowButton(self)
        vBoxLayout.addWidget(self.downArrowButton)

        self.setLayout(vBoxLayout)

    def updateGeometry(self):
        parent = self.parent()
        assert isinstance(parent, QWidget)
        parent_width = parent.width()
        parent_height = parent.height()

        x = parent_width - self.width() - self._marginRight
        y = self._marginTop
        height = parent_height - self._marginTop - self._marginBottom
        self.setGeometry(x, y, self.width(), height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGeometry()
