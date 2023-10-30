from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from typing import List
from galog.app.components.log_messages_pane.data_model import Columns
from galog.app.components.log_messages_pane.delegate import HighlightingData
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.controllers.log_messages_pane.search import SearchResult
from galog.app.highlighting_rules import HighlightingRules
from galog.app.util.colors import logLevelColor


class LogMessageViewPaneController:
    def __init__(self, dataModel: QStandardItemModel, hRules: HighlightingRules):
        self._dataModel = dataModel
        self._hRules = hRules
        self._pane = None

    def takeControl(self, viewPane: LogMessageViewPane):
        self._pane = viewPane
        self._pane.copyButton.clicked.connect(self.copyButtonClicked)

    def _highlightingData(self, row: int) -> HighlightingData:
        return self._dataModel.item(row, Columns.logMessage).data(Qt.UserRole)

    def showContentFor(self, row: int):
        tagName = self._dataModel.item(row, Columns.tagName).text()
        logLevel = self._dataModel.item(row, Columns.logLevel).text()
        logMessage = self._dataModel.item(row, Columns.logMessage).text()
        hData = self._highlightingData(row)

        self._pane.setTag(tagName)
        self._pane.setLogLevel(logLevel)
        self._pane.setLogMessage(logMessage)
        self._pane.setItemBackgroundColor(logLevelColor(logLevel))
        self._pane.applyHighlighting(self._hRules, hData.items)
        self._pane.exec_()

    def copyButtonClickedEnd(self, oldText: str):
        self._pane.copyButton.setEnabled(True)
        self._pane.copyButton.setText(oldText)

    def copyButtonClicked(self):
        self._pane.copyButton.setEnabled(False)
        oldText = self._pane.copyButton.text()
        self._pane.copyButton.setText("Copied")

        clip = QGuiApplication.clipboard()
        clip.setText(self._pane.logMsgTextBrowser.toPlainText())
        QTimer.singleShot(3000, lambda: self.copyButtonClickedEnd(oldText))
