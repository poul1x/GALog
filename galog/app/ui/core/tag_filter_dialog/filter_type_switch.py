from enum import Enum, auto
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

from galog.app.app_state import TagFilteringMode
from galog.app.ui.base.widget import BaseWidget


class FilterTypeSwitch(BaseWidget):
    filterTypeChanged = pyqtSignal(TagFilteringMode)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        filterTypeLabel = QLabel("Filtering mode:")
        self.filterTypeSwitch = QComboBox(self)
        self.filterTypeSwitch.addItem("Disabled")
        self.filterTypeSwitch.addItem("Show matching")
        self.filterTypeSwitch.addItem("Hide matching")
        self.filterTypeSwitch.currentIndexChanged.connect(self._filterTypeChanged)
        self.filterTypeSwitch.setCurrentIndex(TagFilteringMode.Disabled.value)
        hBoxLayout.addWidget(filterTypeLabel)
        hBoxLayout.addWidget(self.filterTypeSwitch)
        hBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setLayout(hBoxLayout)

    def _filterTypeChanged(self, index: int):
        self.filterTypeChanged.emit(TagFilteringMode(index))

    def filteringMode(self):
        return TagFilteringMode(self.filterTypeSwitch.currentIndex())

    def setFilteringMode(self, mode: TagFilteringMode):
        self.filterTypeSwitch.setCurrentIndex(mode.value)
