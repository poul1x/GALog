from typing import Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

from galog.app.paths import iconFile
from galog.app.ui.quick_dialogs import MessageBox


def msgBoxInfo(msgBrief: str, msgVerbose: str, parent: Optional[QWidget] = None):
    messageBox = MessageBox(parent)
    messageBox.setHeaderText(msgBrief)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-info")))
    messageBox.setWindowTitle("Success")
    messageBox.addButton("Ok")
    messageBox.exec_()


def msgBoxErr(msgBrief: str, msgVerbose: str, parent: Optional[QWidget] = None):
    messageBox = MessageBox(parent)
    messageBox.setHeaderText(msgBrief)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-error")))
    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Error")
    messageBox.exec_()


def msgBoxErr2(msgVerbose: str, parent: Optional[QWidget] = None):
    messageBox = MessageBox(parent)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-error")))
    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Error")
    messageBox.exec_()


def msgBoxPrompt(caption: str, body: str, parent: Optional[QWidget] = None):
    messageBox = MessageBox(parent)
    messageBox.setHeaderText(caption)
    messageBox.setBodyText(body)
    messageBox.setIcon(QIcon(iconFile("msgbox-warning")))
    btnIdYes = messageBox.addButton("Yes")
    btnIdNo = messageBox.addButton("No")
    messageBox.setDefaultButton(btnIdNo)
    messageBox.setWindowTitle("User action required")
    return messageBox.exec_() == btnIdYes


def msgBoxNotImp(parent: Optional[QWidget] = None):
    messageBox = MessageBox(parent)
    messageBox.setHeaderText("Feature not implemented")
    messageBox.setBodyText("The feature will be finished soon. Please, be patient")
    messageBox.setIcon(QIcon(iconFile("msgbox-info")))
    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Not implemented")
    messageBox.exec_()
