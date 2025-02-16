from typing import Optional
from PyQt5.QtWidgets import QDialog, QWidget, QApplication
from PyQt5.QtCore import Qt

from .style import GALogStyle


class BaseDialog(QDialog):
    def _defaultFlags(self):
        return (
            Qt.Window
            | Qt.Dialog
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, self._defaultFlags())
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowTitle("GALog")
        self.setStyle(GALogStyle())

    def _parentGeometry(self):
        parent = self.parent()
        if parent is None:
            return QApplication.primaryScreen().geometry()
        else:
            assert isinstance(parent, QWidget)
            return parent.geometry()

    def setRelativeGeometry(
        self,
        relWidth: float,
        relHeight: float,
        minWidth: int,
        minHeight: int,
    ):
        assert relWidth > 0 and relWidth < 1
        assert relHeight > 0 and relHeight < 1

        geometry = self._parentGeometry()
        width = max(int(geometry.width() * relWidth), minWidth)
        height = max(int(geometry.height() * relHeight), minHeight)

        x = geometry.x() + (geometry.width() - width) // 2
        y = geometry.y() + (geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)
