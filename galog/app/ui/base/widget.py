from typing import Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from .style import GALogStyle

class Widget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyle(GALogStyle())

    def refreshStyleSheet(self):
        # Force  to update the stylesheet
        # When dynamic property was changed
        self.setStyleSheet(self.styleSheet())