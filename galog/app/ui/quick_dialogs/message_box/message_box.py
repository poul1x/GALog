from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QCheckBox, QLabel, QVBoxLayout, QWidget

from galog.app.settings import readSettings
from galog.app.ui.base.dialog import Dialog

from .button_bar import ButtonBar
from .content_area import ContentArea


class MessageBox(Dialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = readSettings()
        self._clickedButtonId = -1
        self.setFixedMaxSize(450, 250)
        self.setRelativeGeometry(0.2, 0.3, 450, 250)
        self.setObjectClass("MessageBox")
        self.initUserInterface()

    def checkBox(self):
        return self._checkBox

    def setCheckBox(self, checkBox: QCheckBox):
        #
        # First, own the checkBox,
        # overriding its parent
        #

        layout: QVBoxLayout = self.layout()
        checkBox.setParent(self)

        #
        # Find ButtonBar widget
        #

        index = -1
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget.objectName().startswith("ButtonBar"):
                index = i
                break

        #
        # Insert checkBox right before (above) the ButtonBar
        # If another checkBox has been already set,
        # replace it with new one
        #

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

    def setHeaderText(self, text: str):
        index = 1
        layout: QVBoxLayout = self.layout()
        widget = layout.itemAt(index).widget()

        if isinstance(widget, QLabel):
            widget.setText(text)
            return

        headerTextLabel = QLabel(self)
        headerTextLabel.setAlignment(Qt.AlignCenter)
        headerTextLabel.setObjectName("HeadTextLabel")
        headerTextLabel.setContentsMargins(0, 0, 0, 0)
        headerTextLabel.setFont(self._upsizedFont())
        headerTextLabel.setWordWrap(True)
        headerTextLabel.setText(text)

        layout.insertWidget(index, headerTextLabel)

    def _upsizedFont(self):
        family = self._settings.fonts.standard.family
        size = self._settings.fonts.standard.size + 1
        return QFont(family, size)

    def setBodyText(self, text: str):
        self.contentArea.setBodyText(text)

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout(self)
        self.headEmptySpace = QLabel(self)
        self.headEmptySpace.setObjectName("HeadEmptySpace")
        self.contentArea = ContentArea(self)
        self.buttonBar = ButtonBar(self)
        self.buttonBar.setButtonFont(self._upsizedFont())
        self.buttonBar.buttonClicked.connect(self._onButtonClicked)

        vBoxLayout.addWidget(self.headEmptySpace)
        vBoxLayout.addWidget(self.contentArea, 1)
        vBoxLayout.addWidget(self.buttonBar)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setSpacing(0)
        self.setLayout(vBoxLayout)

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
