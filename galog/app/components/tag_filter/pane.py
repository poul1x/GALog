from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from galog.app.util.paths import iconFile


class TagFilterPane(QDialog):
    def _defaultFlags(self):
        return (
            Qt.Window
            | Qt.Dialog
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.setObjectName("TagFilterPane")
        self.setWindowTitle("Tag Filter")
        self.initUserInterface()

    def initUserInterface(self):
        self.logLevelLabel = QLabel()
        self.logLevelLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logLevelLabel.setFixedWidth(300)
        self.logLevelLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.tagNameLabel = QLabel()
        self.tagNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tagNameLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.copyButton = QPushButton()
        self.copyButton.setIcon(QIcon(iconFile("copy")))
        self.copyButton.setText("Copy contents")
        self.copyButton.setFixedWidth(220)

        self.copyButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.copyButton.setIconSize(QSize(32, 32))

        hLeftBoxLayout = QHBoxLayout()
        hLeftBoxLayout.addWidget(self.logLevelLabel)
        hLeftBoxLayout.addWidget(self.tagNameLabel)
        hLeftBoxLayout.setAlignment(Qt.AlignLeft)

        hRightBoxLayout = QHBoxLayout()
        hRightBoxLayout.addWidget(self.copyButton)
        hRightBoxLayout.setAlignment(Qt.AlignRight)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addLayout(hLeftBoxLayout, 1)
        hBoxLayout.addLayout(hRightBoxLayout)

        self.logMsgTextBrowser = QTextBrowser()
        self.logMsgTextBrowser.setOpenExternalLinks(True)
        self.logMsgTextBrowser.setReadOnly(True)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addWidget(self.logMsgTextBrowser, 1)
        self.setLayout(vBoxLayout)

        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

from PyQt5 import QtCore, QtGui, QtWidgets

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.edit = QtWidgets.QLineEdit()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.edit)
        word_bank =  ['alpha', 'beta', 'vector space']
        self.completer = QtWidgets.QCompleter(word_bank)
        self.completer.setCaseSensitivity(
            QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(QtCore.Qt.MatchFlag.MatchStartsWith)
        self.completer.setWidget(self.edit)
        self.completer.activated.connect(self.handleCompletion)
        self.edit.textChanged.connect(self.handleTextChanged)
        self._completing = False

    def handleTextChanged(self, text):
        if not self._completing:
            found = False
            prefix = text.rpartition(',')[-1]
            if len(prefix) > 1:
                self.completer.setCompletionPrefix(prefix)
                if self.completer.currentRow() >= 0:
                    found = True
            if found:
                self.completer.complete()
            else:
                self.completer.popup().hide()

    def handleCompletion(self, text):
        if not self._completing:
            self._completing = True
            prefix = self.completer.completionPrefix()
            self.edit.setText(self.edit.text()[:-len(prefix)] + text)
            self._completing = False

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    window = Window()
    window.setGeometry(600, 100, 300, 50)
    window.show()
    app.exec()