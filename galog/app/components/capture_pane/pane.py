from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListView,
    QComboBox,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtGui import (
    QKeyEvent,
    QIcon,
    QStandardItemModel,
)

from .header import CapturePaneHeader
from .body import CapturePaneBody
from .footer import CapturePaneFooter

from galog.app.components.reusable.search_input import SearchInput
from galog.app.util.hotkeys import HotkeyHelper
from galog.app.util.paths import iconFile

from enum import Enum, auto


class CapturePane(QDialog):
    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowCloseButtonHint

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.setObjectName("CapturePane")
        self.setAttribute(Qt.WA_StyledBackground)
        self.initUserInterface()
        self.setGeometryAuto()
        self.initFocusPolicy()

    def keyPressEvent(self, event: QKeyEvent):
        helper = HotkeyHelper(event)
        if helper.isCtrlFPressed():
            self.searchInput.setFocus()
        if helper.isCtrlDPressed():
            self.deviceDropDown.showPopup()
        elif helper.isCtrlRPressed():
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

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = CapturePaneHeader(self)
        self.body = CapturePaneBody(self)
        self.footer = CapturePaneFooter(self)

        layout.addWidget(self.header)
        layout.addWidget(self.body)
        layout.addWidget(self.footer)
        self.setLayout(layout)

    def initFocusPolicy(self):
        self.reloadButton.setFocusPolicy(Qt.NoFocus)
        self.deviceDropDown.setFocusPolicy(Qt.NoFocus)
        self.actionDropDown.setFocusPolicy(Qt.NoFocus)
        self.selectButton.setFocusPolicy(Qt.NoFocus)
        self.cancelButton.setFocusPolicy(Qt.NoFocus)
        self.fromApkButton.setFocusPolicy(Qt.NoFocus)

        self.searchInput.setFocus()
        self.setTabOrder(self.searchInput, self.packagesList)
        self.setTabOrder(self.packagesList, self.searchInput)

    @property
    def deviceLabel(self):
        return self.header.deviceLabel

    @property
    def deviceDropDown(self):
        return self.header.deviceDropDown

    @property
    def actionLabel(self):
        return self.header.actionLabel

    @property
    def actionDropDown(self):
        return self.header.actionDropDown

    @property
    def reloadButton(self):
        return self.header.reloadButton

    @property
    def packagesList(self):
        return self.body.packagesList

    @property
    def searchInput(self):
        return self.body.searchInput

    @property
    def dataModel(self):
        return self.body.dataModel

    @property
    def filterModel(self):
        return self.body.filterModel

    @property
    def selectButton(self):
        return self.footer.selectButton

    @property
    def fromApkButton(self):
        return self.footer.fromApkButton

    @property
    def cancelButton(self):
        return self.footer.cancelButton
