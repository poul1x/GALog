from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from galog.app.ui.base.dialog import BaseDialog

class LoadingDialog(BaseDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUserInterface()
        self.adjustSize()
        self.setMinimumWidth(350)
        self.center()

    def center(self):
        mainWindow = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                mainWindow = widget
                break

        assert mainWindow is not None
        mwGeometry = mainWindow.geometry()
        geometry = self.geometry()
        geometry.moveCenter(mwGeometry.center())
        self.move(geometry.topLeft())

    def initUserInterface(self):
        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)

    def initUserInterface(self):
        container = QWidget(self)
        container.setObjectName("Container")
        container.setAttribute(Qt.WA_StyledBackground)

        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        container.setLayout(layout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(container)
        self.setLayout(mainLayout)

    def setText(self, text: str):
        self.label.setText(text)
