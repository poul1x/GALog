from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from galog.app.util.paths import styleSheetFile
from galog.app.util.style import CustomStyle

from .button_bar import MessageBoxButtonBar
from .content_area import MessageBoxContentArea


class MessageBox(QDialog):
    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.3)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def center(self):
        mainWindow = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                mainWindow = widget
                break

        assert mainWindow is not None
        mwGeometry = mainWindow.geometry()
        geometry = self.frameGeometry()
        geometry.moveCenter(mwGeometry.center())
        self.move(geometry.topLeft())

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("MessageBox")
        self.setWindowTitle("GALog")
        self.initUserInterface()
        self.setGeometryAuto()
        self.loadStyleSheet()
        self.setSizeAuto()
        self.center()
        self._clickedButtonId = -1

    def loadStyleSheet(self):
        with open(styleSheetFile("message_box")) as f:
            self.setStyleSheet(f.read())

    def checkBox(self):
        return self._checkBox

    def setCheckBox(self, checkBox: QCheckBox):
        layout: QVBoxLayout = self.layout()
        checkBox.setParent(self)

        index = -1
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget.objectName().startswith("MessageBoxButtonBar"):
                index = i
                break

        assert index > 0
        widget = layout.itemAt(index - 1).widget()
        if isinstance(widget, QCheckBox):
            layout.replaceWidget(widget, checkBox)
        else:
            layout.insertWidget(index, checkBox)

        self._checkBox = checkBox

    def _onButtonClicked(self, buttonId: int):
        self._clickedButtonId = buttonId
        self.accept()

    def setSizeAuto(self):
        self.setMaximumHeight(250)
        self.setMaximumWidth(450)

    def setHeaderText(self, text: str):
        index = 0
        layout: QVBoxLayout = self.layout()
        widget = layout.itemAt(index).widget()

        if isinstance(widget, QLabel):
            widget.setText(text)
            return

        headerTextLabel = QLabel(self)
        headerTextLabel.setAlignment(Qt.AlignCenter)
        headerTextLabel.setObjectName("MessageBoxHeadTextLabel")
        headerTextLabel.setContentsMargins(0, 0, 0, 0)
        headerTextLabel.setWordWrap(True)
        headerTextLabel.setText(text)
        layout.insertWidget(index, headerTextLabel)

    def setBodyText(self, text: str):
        self.contentArea.setBodyText(text)

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout(self)
        self.contentArea = MessageBoxContentArea(self)
        self.buttonBar = MessageBoxButtonBar(self)
        self.buttonBar.buttonClicked.connect(self._onButtonClicked)

        vBoxLayout.addWidget(self.contentArea, 1)
        vBoxLayout.addWidget(self.buttonBar)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)
        self.setLayout(vBoxLayout)
        self.setStyle(CustomStyle())

    def addButton(self, name: str):
        return self.buttonBar.addButton(name)

    def setDefaultButton(self, buttonId: int):
        return self.buttonBar.setDefaultButton(buttonId)

    def setIcon(self, icon: QIcon):
        self.contentArea.setIcon(icon)

    def exec_(self):
        QApplication.beep()
        super().exec_()
        return self._clickedButtonId

    exec = exec_
