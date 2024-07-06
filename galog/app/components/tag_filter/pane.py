from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from galog.app.util.list_view import ListView
from galog.app.util.paths import iconFile

from .filter_type_switch import FilterTypeSwitch
from .control_button_bar import ControlButtonBar
from .bottom_button_bar import BottomButtonBar
from .filtered_tags_list import FilteredTagsList

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
        self.initGeometry()

    def initGeometry(self):
        screen = QApplication.desktop().screenGeometry()
        width = min(int(screen.width() * 0.4), 450)
        height = min(int(screen.height() * 0.4), 400)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def initUserInterface(self):
        filterTypeSwitch = FilterTypeSwitch(self)
        controlButtonBar = ControlButtonBar(self)
        filteredTagsList = FilteredTagsList(self)
        bottomButtonBar = BottomButtonBar(self)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0,10,0,10)
        hBoxLayout.setSpacing(0)
        hBoxLayout.addWidget(filteredTagsList, stretch=1)
        hBoxLayout.addWidget(controlButtonBar)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(0,0,0,0)
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(filterTypeSwitch)
        vBoxLayout.addLayout(hBoxLayout, stretch=1)
        vBoxLayout.addWidget(bottomButtonBar)

        self.setLayout(vBoxLayout)



# from PyQt5 import QtCore, QtGui, QtWidgets

# class Window(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.edit = QtWidgets.QLineEdit()
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.addWidget(self.edit)
#         word_bank =  ['alpha', 'beta', 'vector space']
#         self.completer = QtWidgets.QCompleter(word_bank)
#         self.completer.setCaseSensitivity(
#             QtCore.Qt.CaseSensitivity.CaseInsensitive)
#         self.completer.setFilterMode(QtCore.Qt.MatchFlag.MatchStartsWith)
#         self.completer.setWidget(self.edit)
#         self.completer.activated.connect(self.handleCompletion)
#         self.edit.textChanged.connect(self.handleTextChanged)
#         self._completing = False

#     def handleTextChanged(self, text):
#         if not self._completing:
#             found = False
#             prefix = text.rpartition(',')[-1]
#             if len(prefix) > 1:
#                 self.completer.setCompletionPrefix(prefix)
#                 if self.completer.currentRow() >= 0:
#                     found = True
#             if found:
#                 self.completer.complete()
#             else:
#                 self.completer.popup().hide()

#     def handleCompletion(self, text):
#         if not self._completing:
#             self._completing = True
#             prefix = self.completer.completionPrefix()
#             self.edit.setText(self.edit.text()[:-len(prefix)] + text)
#             self._completing = False

# if __name__ == '__main__':

#     app = QtWidgets.QApplication(['Test'])
#     window = Window()
#     window.setGeometry(600, 100, 300, 50)
#     window.show()
#     app.exec()