from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget

from .style import GALogStyle


class Dialog(QDialog):
    @staticmethod
    def _defaultFlags():
        return (
            Qt.Window
            | Qt.Dialog
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        objectName: Optional[str] = None,
    ):
        super().__init__(parent, self._defaultFlags())
        self.setObjectName(objectName or self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowTitle("GALog")
        self.setStyle(GALogStyle())

    def setFixedMaxSize(self, maxWidth: int, maxHeight: int):
        self.setMaximumWidth(maxWidth)
        self.setMaximumHeight(maxHeight)

    def setFixedMinSize(self, maxWidth: int, maxHeight: int):
        self.setMinimumWidth(maxWidth)
        self.setMinimumHeight(maxHeight)

    def _findMainWindow(self):
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget
        return None

    def _parentGeometry(self):
        parent = self.parent()
        if parent is not None:
            assert isinstance(parent, (QDialog, QMainWindow))
            return parent.frameGeometry()
        else:
            mainWindow = self._findMainWindow()
            assert mainWindow is not None
            return mainWindow.frameGeometry()

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

    def moveToCenter(self):
        geometry = self.geometry()
        parentGeometry = self._parentGeometry()
        geometry.moveCenter(parentGeometry.center())
        self.move(geometry.topLeft())

    def refreshStyleSheet(self):
        # Force  to update the stylesheet
        # When dynamic property was changed
        self.setStyleSheet(self.styleSheet())
