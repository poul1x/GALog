from typing import Optional

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget

from galog.app.settings import readSettings
from galog.app.ui.base.widget import Widget


class ButtonBar(Widget):
    buttonClicked = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._initUserInterface()
        self._settings = readSettings()
        self._buttonCount = 0

    def _initUserInterface(self):
        hBoxLayout = QHBoxLayout(self)
        hBoxLayout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setSpacing(0)
        self.setLayout(hBoxLayout)

    def _setDefaultButtonFont(self, button: QPushButton):
        family = self._settings.fonts.upsized.family
        size = self._settings.fonts.upsized.size
        button.setFont(QFont(family, size))

    def addButton(self, name: str):
        buttonId = self._buttonCount
        button = QPushButton(name, self)
        self._setDefaultButtonFont(button)
        button.clicked.connect(lambda: self.buttonClicked.emit(buttonId))
        self.layout().addWidget(button)
        self._buttonCount += 1
        return buttonId

    def setDefaultButton(self, buttonId: int):
        layout = self.layout()
        assert buttonId >= 0
        assert buttonId < layout.count()

        button = self.layout().itemAt(buttonId).widget()
        assert isinstance(button, QPushButton)
        button.setDefault(True)

    def buttonCount(self):
        return self._buttonCount
