from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from galog.app.util.list_view import ListView
from galog.app.util.paths import iconFile

from .filter_type_switch import FilterTypeSwitch
from .control_button_bar import ControlButtonBar
from .bottom_button_bar import BottomButtonBar
from .filtered_tags_list import FilteredTagsList

class TagFilterPane(QDialog):
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
        filterTypeSwitch = FilterTypeSwitch(self)
        controlButtonBar = ControlButtonBar(self)
        filteredTagsList = FilteredTagsList(self)
        bottomButtonBar = BottomButtonBar(self)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0,10,0,10)
        hBoxLayout.setSpacing(0)
        hBoxLayout.addWidget(filteredTagsList, stretch=1)
        hBoxLayout.addWidget(controlButtonBar)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(0,0,0,0)
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(filterTypeSwitch)
        vBoxLayout.addLayout(hBoxLayout, stretch=1)
        vBoxLayout.addWidget(bottomButtonBar)

        self.setLayout(vBoxLayout)