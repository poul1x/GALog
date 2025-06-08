from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from galog.app.ui.base.widget import Widget


class ControlButtonBar(Widget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(10, 0, 10, 0)
        self.addTagButton = QPushButton("Add", self)
        self.removeTagButton = QPushButton("Remove", self)
        self.removeAllTagsButton = QPushButton("Remove all", self)
        self.saveToFileButton = QPushButton("Save to file", self)
        self.loadFromFileButton = QPushButton("Load from file", self)
        vBoxLayout.addWidget(self.addTagButton)
        vBoxLayout.addWidget(self.removeTagButton)
        vBoxLayout.addWidget(self.removeAllTagsButton)
        vBoxLayout.addWidget(self.saveToFileButton)
        vBoxLayout.addWidget(self.loadFromFileButton)
        vBoxLayout.setAlignment(Qt.AlignTop)
        self.setLayout(vBoxLayout)
