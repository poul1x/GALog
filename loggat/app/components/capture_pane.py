from typing import List, Optional
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from loggat.app.util.paths import iconFile
from loggat.app.util.signals import blockSignals


class MyProxyStyle(QProxyStyle):
    def standardIcon(self, standardIcon, option=None, widget=None):
        if standardIcon == QStyle.SP_LineEditClearButton:
            return QIcon(iconFile("clear"))
        return super().standardIcon(standardIcon, option, widget)


class MyListView(QListView):
    itemActivated = pyqtSignal(QModelIndex)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.itemActivated.emit(self.currentIndex())
            event.accept()
            return
        super().keyPressEvent(event)


class CapturePane(QDialog):
    deviceChanged = pyqtSignal(str)
    packageSelected = pyqtSignal(str)
    packageNameFromApk = pyqtSignal()

    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowCloseButtonHint

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.initUserInterface()
        self.setGeometryAuto()
        self.selectedPackageName = None

    def setGeometryAuto(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.3)
        height = int(screen.height() * 0.4)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def setDevices(self, devices: List[str]):
        with blockSignals(self.deviceDropDown):
            self.model.removeRows(0, self.model.rowCount())
            self.deviceDropDown.addItems(devices)

    def setPackagesEmpty(self):
        self.model.removeRows(0, self.model.rowCount())
        item = QStandardItem()
        item.setSelectable(False)
        item.setEnabled(False)
        self.model.appendRow(item)

        item = QStandardItem("¯\_(ツ)_/¯")
        item.setSelectable(False)
        item.setEnabled(False)
        item.setData(Qt.AlignCenter, Qt.TextAlignmentRole)
        font = QFont("Arial")
        font.setPointSize(12)
        item.setFont(font)
        self.model.appendRow(item)

        self.selectButton.setEnabled(False)
        self.fromApkButton.setEnabled(False)

    def setPackages(self, packages: List[str]):
        assert len(packages) > 0, "Non empty list expected"
        self.model.removeRows(0, self.model.rowCount())

        for package in packages:
            self.model.appendRow(QStandardItem(package))

        index = self.proxyModel.index(0, 0)
        self._selectIndex(index)

        self.selectButton.setEnabled(True)
        self.fromApkButton.setEnabled(True)

    def clearPackages(self):
        self.model.removeRows(0, self.model.rowCount())

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
        self.deviceDropDown.currentTextChanged.connect(self.onDeviceChanged)

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

        self.packagesListView = MyListView(self)
        self.packagesListView.setEditTriggers(QListView.NoEditTriggers)
        self.packagesListView.doubleClicked.connect(self.onPackageSelected)
        self.packagesListView.itemActivated.connect(self.onPackageSelected)
        self.packagesListView.setStyleSheet("QListView::item:selected { background-color: #CDE3FF; color: highlightedText;}")

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
        self.searchLineEdit.addAction(
            QIcon(iconFile("search")), QLineEdit.LeadingPosition
        )
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

    def onPackageSelected(self, index: QModelIndex):
        model = self.packagesListView.model()
        self.packageSelected.emit(model.data(index))
        self.accept()

    def fromApkButtonClicked(self):
        self.packageNameFromApk.emit()

    def onDeviceChanged(self, newDevice: str):
        self.deviceChanged.emit(newDevice)

    def reloadButtonClicked(self):
        self.selectButton.setEnabled(False)
        self.fromApkButton.setEnabled(False)
        device = self.deviceDropDown.currentText()
        self.onDeviceChanged(device)

    def cancelButtonClicked(self):
        self.reject()

    def selectButtonClicked(self):
        self.onPackageSelected(self.packagesListView.currentIndex())

    def selectedPackage(self):
        index = self.packagesListView.currentIndex()
        return index.data() if index.isValid() else None

    def selectedDevice(self):
        return self.deviceDropDown.currentText()

    def setSelectedDevice(self, deviceName: str):
        with blockSignals(self.deviceDropDown):
            self.deviceDropDown.setCurrentText(deviceName)

    def _selectIndex(self, index: QModelIndex):
        selectionModel = self.packagesListView.selectionModel()
        selectionModel.clear()

        self.packagesListView.setCurrentIndex(index)
        selectionModel.select(index, QItemSelectionModel.Select)
        self.packagesListView.scrollTo(index, QListView.PositionAtCenter)

    def setSelectedPackage(self, packageName: str):
        items = self.model.findItems(packageName, Qt.MatchExactly)
        if items:
            index = items[0].index()
            proxyIndex = self.proxyModel.mapFromSource(index)
            self._selectIndex(proxyIndex)

    def isPackageInstalled(self, packageName: str):
        items = self.model.findItems(packageName, Qt.MatchExactly)
        return bool(items)

