from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class ControlButtonBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
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
