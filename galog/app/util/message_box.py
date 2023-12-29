from typing import Optional

from galog.app.components.dialogs import MessageBox


def showInfoMsgBox(msgBrief: str, msgVerbose: str):
    messageBox = MessageBox()
    messageBox.setText(msgBrief)
    messageBox.setInformativeText(msgVerbose)
    messageBox.setStandardButtons(MessageBox.Ok)
    messageBox.setWindowTitle("Success")
    messageBox.setBeepEnabled(False)
    messageBox.exec_()


def showErrorMsgBox(msgBrief: str, msgVerbose: str, details: Optional[str] = None):
    messageBox = MessageBox()
    messageBox.setText(msgBrief)
    messageBox.setInformativeText(msgVerbose)

    if details:
        messageBox.setDetailedText(details)

    messageBox.setStandardButtons(MessageBox.Ok)
    messageBox.setWindowTitle("Error")
    messageBox.exec_()


def showPromptMsgBox(title: str, caption: str, body: str):
    messageBox = MessageBox()
    messageBox.setText(caption)
    messageBox.setInformativeText(body)
    messageBox.setStandardButtons(MessageBox.Yes | MessageBox.No)
    messageBox.setDefaultButton(MessageBox.No)
    messageBox.setWindowTitle(title)
    return messageBox.exec_() == MessageBox.Yes


def showNotImpMsgBox():
    messageBox = MessageBox()
    messageBox.setText("Feature not implemented")
    messageBox.setInformativeText(
        "The feature will be finished soon. Please, be patient"
    )
    messageBox.setStandardButtons(MessageBox.Ok)
    messageBox.setWindowTitle("Not implemented")
    messageBox.exec_()
