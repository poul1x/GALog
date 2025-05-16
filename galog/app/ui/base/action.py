from typing import Optional
from galog.app.msgbox import msgBoxErr as _msgBoxErr
from galog.app.msgbox import msgBoxPrompt as _msgBoxPrompt
from galog.app.ui.quick_dialogs import LoadingDialog

from PyQt5.QtWidgets import QWidget


class BaseAction:
    def __init__(self, parentWidget: Optional[QWidget] = None):
        self._parentWidget = parentWidget
        self._loadingDialog = LoadingDialog(parentWidget)
        self._loadingDialog.setText(self.__class__.__name__)
        self._success = None

    def _closeLoadingDialog(self):
        self._loadingDialog.close()

    def _execLoadingDialog(self):
        self._loadingDialog.exec_()

    def _setLoadingDialogText(self, text: str):
        self._loadingDialog.setText(text)

    def _succeededSafe(self):
        assert (
            self._success is not None
        ), "Call setSucceeded or setFailed before using this"
        return self._success

    def succeeded(self):
        return self._succeededSafe()

    def failed(self):
        return not self._succeededSafe()

    def _setSucceeded(self):
        self._closeLoadingDialog()
        self._success = True

    def _setFailed(self):
        self._closeLoadingDialog()
        self._success = False

    def _msgBoxErr(self, msgBrief: str, msgVerbose: str):
        _msgBoxErr(msgBrief, msgVerbose, self._parentWidget)

    def _msgBoxPrompt(self, msgBrief: str, msgVerbose: str):
        return _msgBoxPrompt(msgBrief, msgVerbose, self._parentWidget)
