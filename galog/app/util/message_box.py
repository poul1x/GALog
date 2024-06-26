from typing import Optional

from galog.app.components.dialogs import MessageBox
from PyQt5.QtGui import QIcon

from galog.app.util.paths import iconFile


def showInfoMsgBox(msgBrief: str, msgVerbose: str):
    messageBox = MessageBox()
    messageBox.setHeaderText(msgBrief)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-info")))
    messageBox.setWindowTitle("Success")
    messageBox.addButton("Ok")
    messageBox.exec_()


def showErrorMsgBox(msgBrief: str, msgVerbose: str, details: Optional[str] = None):
    messageBox = MessageBox()
    messageBox.setHeaderText(msgBrief)
    messageBox.setBodyText(msgVerbose)
    messageBox.setIcon(QIcon(iconFile("msgbox-error")))

    # if details:
    #     messageBox.setDetailedText(details)

    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Error")
    messageBox.exec_()


def showPromptMsgBox(title: str, caption: str, body: str):
    messageBox = MessageBox()
    messageBox.setHeaderText(caption)
    messageBox.setBodyText(body)
    messageBox.setIcon(QIcon(iconFile("msgbox-warning")))
    btnIdYes = messageBox.addButton("Yes")
    btnIdNo = messageBox.addButton("No")
    messageBox.setDefaultButton(btnIdNo)
    messageBox.setWindowTitle(title)
    return messageBox.exec_() == btnIdYes


def showNotImpMsgBox():
    messageBox = MessageBox()
    messageBox.setHeaderText("Feature not implemented")
    messageBox.setBodyText(
        "The feature will be finished soon. Please, be patient"
    )
    messageBox.setIcon(QIcon(iconFile("msgbox-info")))
    messageBox.addButton("Ok")
    messageBox.setWindowTitle("Not implemented")
    messageBox.exec_()
