
from typing import List, Optional
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from loggat.app.util.paths import iconFile

class MyProxyStyle(QProxyStyle):
    def standardIcon(self, standardIcon, option=None, widget=None):
        if standardIcon == QStyle.SP_LineEditClearButton:
            return QIcon(iconFile("clear"))
        return super().standardIcon(standardIcon, option, widget)

class NewCapturePane(QDialog):

    deviceChanged = pyqtSignal(str)
    packageSelected = pyqtSignal(str)

    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowCloseButtonHint

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.initUserInterface()
        self.setGeometryAuto()

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.3)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def setDevices(self, devices: List[str]):
        assert len(devices) > 0, "At least one device required"
        self.deviceDropDown.addItems(devices)

    def setPackages(self, packages: List[str]):
        self.model.removeRows(0, self.model.rowCount())
        for package in packages:
            self.model.appendRow(QStandardItem(package))
        if len(packages) > 0:
            index = self.packagesListView.model().index(0, 0)
            self.packagesListView.setCurrentIndex(index)
            self.selectButton.setEnabled(True)

    def initUserInterface(self):
        self.setWindowTitle("New capture")
        self.setMinimumHeight(200)
        self.setMinimumWidth(100)

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
        self.deviceDropDown.currentIndexChanged.connect(self.deviceSelected)
        self.reloadButton = QPushButton(self)
        self.reloadButton.setIcon(QIcon(iconFile("reload")))
        self.reloadButton.setText("Reload packages")
        self.reloadButton.clicked.connect(self.reloadButtonClicked)

        hBoxLayoutTopLeft.addWidget(self.deviceLabel)
        hBoxLayoutTopLeft.addWidget(self.deviceDropDown)
        hBoxLayoutTopRight.addWidget(self.reloadButton)
        hBoxLayoutTop.addLayout(hBoxLayoutTopLeft)
        hBoxLayoutTop.addLayout(hBoxLayoutTopRight)
        vBoxLayout.addLayout(hBoxLayoutTop)

        self.packagesListView = QListView(self)
        self.packagesListView.setEditTriggers(QListView.NoEditTriggers)
        self.model = QStandardItemModel(self)
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setDynamicSortFilter(True)
        self.packagesListView.setModel(self.proxyModel)
        vBoxLayout.addWidget(self.packagesListView)

        self.searchLineEdit = QLineEdit(self)
        self.searchLineEdit.textChanged.connect(self.proxyModel.setFilterFixedString)
        self.searchLineEdit.setPlaceholderText("Search package")
        self.searchLineEdit.addAction(QIcon(iconFile("search")), QLineEdit.LeadingPosition)
        self.searchLineEdit.setStyle(MyProxyStyle(self.searchLineEdit.style()))
        self.searchLineEdit.setClearButtonEnabled(True)
        vBoxLayout.addWidget(self.searchLineEdit)

        self.selectButton = QPushButton("Select")
        self.selectButton.clicked.connect(self.selectButtonClicked)
        self.selectButton.setEnabled(False)
        self.selectButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hBoxLayoutBottomLeft.addWidget(self.selectButton)

        self.fromApkButton = QPushButton("From APK")
        self.fromApkButton.clicked.connect(self.fromApkButtonClicked)
        self.fromApkButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hBoxLayoutBottomLeft.addWidget(self.fromApkButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        hBoxLayoutBottomRight.addWidget(self.cancelButton)

        hBoxLayoutBottom.addLayout(hBoxLayoutBottomLeft)
        hBoxLayoutBottom.addLayout(hBoxLayoutBottomRight)
        vBoxLayout.addLayout(hBoxLayoutBottom)
        self.setLayout(vBoxLayout)

    def fromApkButtonClicked(self):
        pass

    def reloadButtonClicked(self):
        pass

    def cancelButtonClicked(self):
        pass

    def selectButtonClicked(self):
        pass

    def deviceSelected(self, index: QModelIndex):
        selectedItem = self.deviceDropDown.itemText(index)
        print(f"Selected Item: {selectedItem}")
