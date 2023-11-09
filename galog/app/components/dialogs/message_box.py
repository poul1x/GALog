from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
from PyQt5.QtGui import QIcon

from galog.app.util.paths import iconFile, styleSheetFile
from galog.app.util.style import CustomStyle

class MessageBox(QMessageBox):
    def __init__(self):
        super().__init__()
        self.initUserInterface()
        self.setStyle(CustomStyle())

    def initUserInterface(self):
        self.setWindowIcon(QIcon(iconFile("galog")))
        self.buttonBox = self.findChild(QWidget, "qt_msgbox_buttonbox")
        self.buttonBox.setAttribute(Qt.WA_StyledBackground)

        with open(styleSheetFile("message_box")) as f:
            self.setStyleSheet(f.read())

    def exec_(self):
        #
        # QMessageBox resets its layout when
        # setText or setInformativeText methods are called.
        # So, if we want to remove contents margins and spacing
        # in grid layout, we must call appropriate functions
        # there, just before exec() call.
        #

        QApplication.beep()
        self.buttonBox.layout().setContentsMargins(0,0,0,0)
        self.buttonBox.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        return super().exec_()