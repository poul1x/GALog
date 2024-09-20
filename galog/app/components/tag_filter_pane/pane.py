from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .bottom_button_bar import BottomButtonBar
from .control_button_bar import ControlButtonBar
from .filter_type_switch import FilterTypeSwitch
from .filtered_tags_list import FilteredTagsList
from .tag_name_input import TagNameInput


class TagFilterPane(QDialog):
    Accepted = 1
    Rejected = 0

    def _defaultFlags(self):
        return (
            Qt.Window
            | Qt.Dialog
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.setObjectName("TagFilterPane")
        self.setWindowTitle("Tag Filter")
        self.initUserInterface()
        self.initGeometry()

    def initGeometry(self):
        screen = QApplication.desktop().screenGeometry()
        width = min(int(screen.width() * 0.4), 450)
        height = min(int(screen.height() * 0.4), 400)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def initUserInterface(self):
        self.filterTypeSwitch = FilterTypeSwitch(self)
        self.controlButtonBar = ControlButtonBar(self)
        self.tagNameInput = TagNameInput(self)
        self.filteredTagsList = FilteredTagsList(self)
        self.bottomButtonBar = BottomButtonBar(self)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(10, 0, 10, 0)
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(self.tagNameInput)
        vBoxLayout.addWidget(self.filteredTagsList)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 10, 0, 10)
        hBoxLayout.setSpacing(0)
        hBoxLayout.addLayout(vBoxLayout, stretch=1)
        hBoxLayout.addWidget(self.controlButtonBar)

        vBoxLayoutMain = QVBoxLayout()
        vBoxLayoutMain.setContentsMargins(0, 0, 0, 0)
        vBoxLayoutMain.setSpacing(0)
        vBoxLayoutMain.addWidget(self.filterTypeSwitch)
        vBoxLayoutMain.addLayout(hBoxLayout, stretch=1)
        vBoxLayoutMain.addWidget(self.bottomButtonBar)
        self.setLayout(vBoxLayoutMain)

    def exec(self) -> int:
        result = super().exec()
        if result == QDialog.Accepted:
            return TagFilterPane.Accepted
        else:
            return TagFilterPane.Rejected