from galog.app.components.dialogs import MessageBox


def showErrorMsgBox(msgBrief: str, msgVerbose: str):
    messageBox = MessageBox()
    messageBox.setText(msgBrief)
    messageBox.setInformativeText(msgVerbose)
    messageBox.setStandardButtons(MessageBox.Ok)
    messageBox.setWindowTitle("Error")
    messageBox.exec_()

def showQuitMsgBox():
    messageBox = MessageBox()
    messageBox.setText("Do you really want to quit?")
    messageBox.setInformativeText("If you close the window, current progress will be lost")
    messageBox.setStandardButtons(MessageBox.Yes | MessageBox.No)
    messageBox.setDefaultButton(MessageBox.No)
    messageBox.setWindowTitle("Close window")
    return messageBox.exec_() == MessageBox.Yes

def showNotImpMsgBox():
    messageBox = MessageBox()
    messageBox.setText("Feature not implemented")
    messageBox.setInformativeText("The feature will be finished soon. Please, be patient")
    messageBox.setStandardButtons(MessageBox.Ok)
    messageBox.setWindowTitle("Not implemented")
    messageBox.exec_()