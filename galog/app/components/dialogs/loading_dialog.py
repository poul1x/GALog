from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QMainWindow,
    QProgressBar,
    QVBoxLayout,
)

from galog.app.util.paths import styleSheetFile
from galog.app.util.style import CustomStyle


class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyle(CustomStyle())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setObjectName("LoadingDialog")
        self.initUserInterface()
        self.loadStyleSheet()

    def loadStyleSheet(self):
        with open(styleSheetFile("loading_dialog")) as f:
            self.setStyleSheet(f.read())

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
        self.adjustSize()
        self.setMinimumWidth(350)
        # self.setFixedHeight(180)
        self.center()

    def setText(self, text: str):
        self.label.setText(text)
