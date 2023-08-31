import sys
from PyQt5.QtWidgets import QApplication
from .components.main_window import MainWindow

def runApp():

    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec())