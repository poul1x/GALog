from typing import Optional

from PyQt5.QtGui import QIcon

from galog.app.ui.quick_dialogs import MessageBox
from galog.app.paths import iconFile


def msgBoxInfo(msgBrief: str, msgVerbose: str):
    messageBox = MessageBox()
    messageBox.setHeaderText(msgBrief)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-info")))
    messageBox.setWindowTitle("Success")
    messageBox.addButton("Ok")
    messageBox.exec_()


def msgBoxErr(msgBrief: str, msgVerbose: str, details: Optional[str] = None):
    messageBox = MessageBox()
    messageBox.setHeaderText(msgBrief)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-error")))

    # if details:
    #     messageBox.setDetailedText(details)

    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Error")
    messageBox.exec_()


def msgBoxErr2(msgVerbose: str):
    messageBox = MessageBox()
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-error")))
    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Error")
    messageBox.exec_()


def msgBoxPrompt(caption: str, body: str):
    messageBox = MessageBox()
    messageBox.setHeaderText(caption)
    messageBox.setBodyText(body)
    messageBox.setIcon(QIcon(iconFile("msgbox-warning")))
    btnIdYes = messageBox.addButton("Yes")
    btnIdNo = messageBox.addButton("No")
    messageBox.setDefaultButton(btnIdNo)
    messageBox.setWindowTitle("User action required")
    return messageBox.exec_() == btnIdYes


def msgBoxNotImp():
    messageBox = MessageBox()
    messageBox.setHeaderText("Feature not implemented")
    messageBox.setBodyText("The feature will be finished soon. Please, be patient")
    messageBox.setIcon(QIcon(iconFile("msgbox-info")))
    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Not implemented")
    messageBox.exec_()
