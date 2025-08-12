from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget

from galog.app.ui.base.widget import Widget


class BottomButtonBar(Widget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._initUserInterface()

    def _initUserInterface(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.applyButton = QPushButton("Apply")
        self.applyButton.setProperty("name", "apply")
        self.applyButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.applyButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setProperty("name", "cancel")
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.cancelButton)
        self.setLayout(layout)
