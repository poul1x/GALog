from typing import Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from .style import GALogStyle

class BaseWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyle(GALogStyle())