from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from galog.app.util.list_view import ListView
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
        self.initGeometry()

    def initGeometry(self):
        screen = QApplication.desktop().screenGeometry()
        width = min(int(screen.width() * 0.4), 450)
        height = min(int(screen.height() * 0.4), 400)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def initUserInterface(self):
        hBoxLayout = QHBoxLayout()
        filterTypeLabel = QLabel("Filter type")
        filterTypeSelector = QComboBox(self)
        filterTypeSelector.addItem("Include")
        filterTypeSelector.addItem("Exclude")
        hBoxLayout.addWidget(filterTypeLabel)
        hBoxLayout.addWidget(filterTypeSelector)

        vBoxLayout = QVBoxLayout()
        self.addTagButton = QPushButton("Add", self)
        self.removeTagButton = QPushButton("Remove", self)
        self.removeAllTagsButton = QPushButton("Remove all", self)
        self.saveToFileButton = QPushButton("Save to file",self)
        self.loadFromFileButton = QPushButton("Load from file", self)
        vBoxLayout.addWidget(self.removeTagButton)
        vBoxLayout.addWidget(self.removeAllTagsButton)
        vBoxLayout.addWidget(self.saveToFileButton)
        vBoxLayout.addWidget(self.loadFromFileButton)


        hBoxLayout4 = QHBoxLayout()
        self.tagNameInput = QLineEdit(self)
        self.tagNameInput.setPlaceholderText("Enter tag to add")
        hBoxLayout4.addWidget(self.tagNameInput)
        hBoxLayout4.addWidget(self.addTagButton)


        vBoxLayout2  = QVBoxLayout()
        self.tagListView = ListView(self)
        self.tagListView.setEditTriggers(QListView.NoEditTriggers)

        self.dataModel = QStandardItemModel(self)
        self.tagListView.setModel(self.dataModel)
        vBoxLayout2.addWidget(self.tagNameInput)
        vBoxLayout2.addWidget(self.tagListView)

        hBoxLayout2 = QHBoxLayout()
        hBoxLayout2.addLayout(vBoxLayout2)
        hBoxLayout2.addLayout(vBoxLayout)


        hBoxLayout3 = QHBoxLayout()
        buttonSave = QPushButton("Save", self)
        buttonCancel = QPushButton("Cancel", self)
        hBoxLayout3.setAlignment(Qt.AlignRight)
        hBoxLayout3.addWidget(buttonSave)
        hBoxLayout3.addWidget(buttonCancel)

        vBoxLayout3 = QVBoxLayout()
        vBoxLayout3.addLayout(hBoxLayout)
        vBoxLayout3.addLayout(hBoxLayout4)
        vBoxLayout3.addLayout(hBoxLayout2)
        vBoxLayout3.addLayout(hBoxLayout3)
        self.setLayout(vBoxLayout3)



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