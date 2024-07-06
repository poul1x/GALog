from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from enum import Enum, auto

class TagFilterType(int, Enum):
    Include = 0
    Exclude = auto()


class FilterTypeSwitch(QWidget):

    filterTypeChanged = pyqtSignal(TagFilterType)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0,0,0,0)
        # hBoxLayout.setSpacing(0)
        filterTypeLabel = QLabel("Filter type:")
        self.filterTypeSwitch = QComboBox(self)
        self.filterTypeSwitch.addItem("Include")
        self.filterTypeSwitch.addItem("Exclude")
        self.filterTypeSwitch.currentIndexChanged.connect(self._handleCurrentIndexChanged)
        self.filterTypeSwitch.setCurrentIndex(TagFilterType.Exclude.value)
        hBoxLayout.addWidget(filterTypeLabel)
        hBoxLayout.addWidget(self.filterTypeSwitch)
        hBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setLayout(hBoxLayout)

    def _handleCurrentIndexChanged(self, index: int):
        self.filterTypeChanged.emit(TagFilterType(index))

    def filterType(self):
        return TagFilterType(self.filterTypeSwitch.currentIndex())