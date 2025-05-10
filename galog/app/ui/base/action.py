from galog.app.ui.quick_dialogs import LoadingDialog


class BaseAction:
    def __init__(self):
        self._initLoadingDialog(self.__class__.__name__)
        self._success = None

    def _initLoadingDialog(self, text: str):
        self._loadingDialog = LoadingDialog()
        self._loadingDialog.setText(text)

    def _closeLoadingDialog(self):
        self._loadingDialog.close()

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
