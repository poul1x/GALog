from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from galog.app.util.paths import iconFile


class TagFilterButtonBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout(self)
        self.addTagButton = QPushButton(self)
        self.removeTagButton = QPushButton(self)
        self.saveToFileButton = QPushButton(self)
        self.loadFromFileButton = QPushButton(self)
        vBoxLayout.addWidget(self.addTagButton)
        vBoxLayout.addWidget(self.removeTagButton)
        vBoxLayout.addWidget(self.saveToFileButton)
        vBoxLayout.addWidget(self.loadFromFileButton)
        self.setLayout(vBoxLayout)