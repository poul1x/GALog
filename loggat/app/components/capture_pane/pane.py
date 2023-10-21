from typing import List, Optional
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from loggat.app.components.reusable.search_input import SearchInput
from loggat.app.util.hotkeys import HotkeyHelper

from loggat.app.util.paths import iconFile
from loggat.app.util.signals import blockSignals


class CapturePane(QDialog):

    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowCloseButtonHint

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.initUserInterface()
        self.setGeometryAuto()
        self.selectedPackageName = None

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlDPressed():
            self.deviceDropDown.setFocus()
            self.deviceDropDown.showPopup()
        if helper.isCtrlRPressed():
            self.reloadButton.clicked.emit()
        else:
            super().keyPressEvent(event)

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.3)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def initUserInterface(self):
        self.setWindowTitle("New capture")
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)

        vBoxLayout = QVBoxLayout()
        hBoxLayoutTop = QHBoxLayout()
        hBoxLayoutBottom = QHBoxLayout()
        hBoxLayoutTopLeft = QHBoxLayout()
        hBoxLayoutTopLeft.setAlignment(Qt.AlignLeft)
        hBoxLayoutTopRight = QHBoxLayout()
        hBoxLayoutTopRight.setAlignment(Qt.AlignRight)
        hBoxLayoutBottomLeft = QHBoxLayout()
        hBoxLayoutBottomLeft.setAlignment(Qt.AlignLeft)
        hBoxLayoutBottomRight = QHBoxLayout()
        hBoxLayoutBottomRight.setAlignment(Qt.AlignRight)

        self.deviceLabel = QLabel(self)
        self.deviceLabel.setText("Device:")

        self.deviceDropDown = QComboBox(self)

        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload packages")

        hBoxLayoutTopLeft.addWidget(self.deviceLabel)
        hBoxLayoutTopLeft.addWidget(self.deviceDropDown)
        hBoxLayoutTopRight.addWidget(self.reloadButton)
        hBoxLayoutTop.addLayout(hBoxLayoutTopLeft)
        hBoxLayoutTop.addLayout(hBoxLayoutTopRight)
        vBoxLayout.addLayout(hBoxLayoutTop)

        self.packagesList = QListView(self)
        self.packagesList.setEditTriggers(QListView.NoEditTriggers)
        self.packagesList.setStyleSheet("QListView::item:selected { background-color: #CDE3FF; color: highlightedText;}")
        self.packagesList.setFocus()

        self.dataModel = QStandardItemModel(self)
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setSourceModel(self.dataModel)
        self.filterModel.setDynamicSortFilter(True)
        self.packagesList.setModel(self.filterModel)
        vBoxLayout.addWidget(self.packagesList)

        self.searchInput = SearchInput(self)
        self.searchInput.textChanged.connect(self.filterModel.setFilterFixedString)
        self.searchInput.setPlaceholderText("Search package")
        vBoxLayout.addWidget(self.searchInput)

        self.selectButton = QPushButton("Select")
        self.selectButton.setEnabled(False)
        self.selectButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hBoxLayoutBottomLeft.addWidget(self.selectButton)

        self.fromApkButton = QPushButton("From APK")
        self.fromApkButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hBoxLayoutBottomLeft.addWidget(self.fromApkButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hBoxLayoutBottomRight.addWidget(self.cancelButton)

        hBoxLayoutBottom.addLayout(hBoxLayoutBottomLeft)
        hBoxLayoutBottom.addLayout(hBoxLayoutBottomRight)
        vBoxLayout.addLayout(hBoxLayoutBottom)
        self.setLayout(vBoxLayout)


