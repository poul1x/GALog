from galog.app.components.dialogs import MessageBox


def showErrorMsgBox(msgBrief: str, msgVerbose: str):
    messageBox = MessageBox()
    messageBox.setText(msgBrief)
    messageBox.setInformativeText(msgVerbose)
    messageBox.setStandardButtons(MessageBox.Ok)
    messageBox.setWindowTitle("Error")
    messageBox.exec_()