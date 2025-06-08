from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

from galog.app.app_state import TagFilteringMode
from galog.app.ui.base.widget import Widget


class FilterTypeSwitch(Widget):
    filterTypeChanged = pyqtSignal(TagFilteringMode)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setLayout(hBoxLayout)

        self.label = QLabel("Filtering mode:")
        hBoxLayout.addWidget(self.label)

        self.dropdown = QComboBox(self)
        self.dropdown.addItem("Disabled")
        self.dropdown.addItem("Show matching")
        self.dropdown.addItem("Hide matching")
        self.dropdown.currentIndexChanged.connect(self._filterTypeChanged)
        self.dropdown.setCurrentIndex(TagFilteringMode.Disabled.value)
        hBoxLayout.addWidget(self.dropdown)

    def _filterTypeChanged(self, index: int):
        self.filterTypeChanged.emit(TagFilteringMode(index))

    def filteringMode(self):
        return TagFilteringMode(self.dropdown.currentIndex())

    def setFilteringMode(self, mode: TagFilteringMode):
        self.dropdown.setCurrentIndex(mode.value)
