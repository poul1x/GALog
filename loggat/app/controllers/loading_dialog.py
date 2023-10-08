from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class LoadingDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Set range to make it indeterminate
        self.progress_bar.setStyleSheet("margin: 0px; padding: 0px;")
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication()
    window = LoadingDialog()
    window.setWindowTitle('Frameless QDialog with Indeterminate ProgressBar Example')
    window.setGeometry(100, 100, 400, 100)
    window.show()
    app.exec_()
