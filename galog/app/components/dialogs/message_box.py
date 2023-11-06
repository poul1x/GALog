from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
from PyQt5.QtGui import QIcon

from galog.app.util.paths import iconFile, styleSheetFile

class MessageBox(QMessageBox):
    def __init__(self):
        super().__init__()
        self.initUserInterface()

    def initUserInterface(self):
        self.setWindowIcon(QIcon(iconFile("galog")))
        buttonBox = self.findChild(QWidget, "qt_msgbox_buttonbox")
        buttonBox.setAttribute(Qt.WA_StyledBackground)

        with open(styleSheetFile("message_box")) as f:
            self.setStyleSheet(f.read())

    def exec_(self):
        QApplication.beep()
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        return super().exec_()