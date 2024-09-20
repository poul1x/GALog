from enum import Enum, auto

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget


class TagFilteringMode(int, Enum):
    Disabled = 0
    ShowMatching = auto()
    HideMatching = auto()


class FilterTypeSwitch(QWidget):
    filterTypeChanged = Signal(TagFilteringMode)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        filterTypeLabel = QLabel("Filtering mode:")
        self.filterTypeSwitch = QComboBox(self)
        self.filterTypeSwitch.addItem("Disabled")
        self.filterTypeSwitch.addItem("Show matching")
        self.filterTypeSwitch.addItem("Hide matching")
        self.filterTypeSwitch.currentIndexChanged.connect(
            self._handleCurrentIndexChanged
        )
        self.filterTypeSwitch.setCurrentIndex(TagFilteringMode.Disabled.value)
        hBoxLayout.addWidget(filterTypeLabel)
        hBoxLayout.addWidget(self.filterTypeSwitch)
        hBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setLayout(hBoxLayout)

    def _handleCurrentIndexChanged(self, index: int):
        self.filterTypeChanged.emit(TagFilteringMode(index))

    def filteringMode(self):
        return TagFilteringMode(self.filterTypeSwitch.currentIndex())

    def setFilteringMode(self, mode: TagFilteringMode):
        self.filterTypeSwitch.setCurrentIndex(mode.value)
