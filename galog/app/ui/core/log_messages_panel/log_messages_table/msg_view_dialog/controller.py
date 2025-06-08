from copy import deepcopy
from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QStandardItemModel,
    QTextCharFormat,
    QTextCursor,
)

from ..data_model import Column
from ..delegate import HighlightingData
from .msg_view_dialog import LogMessageViewDialog
from ..log_messages_table.pattern_search_task import PatternSearchResult
from galog.app.hrules import HRulesStorage
from galog.app.ui.core.log_messages_panel.log_messages_table.colors import logLevelColor, logLevelColorDarker
from galog.app.paths import styleSheetFile


class LogMessageViewPaneController:
    QSS_TEMPLATE: Optional[str] = None

    @staticmethod
    def _loadStyleSheet():
        if not LogMessageViewPaneController.QSS_TEMPLATE:
            path = styleSheetFile("log_message_view_dialog")
            with open(path, "r", encoding="utf-8") as f:
                LogMessageViewPaneController.QSS_TEMPLATE = f.read()

    def __init__(self, dataModel: QStandardItemModel, hRules: HRulesStorage):
        self._loadStyleSheet()
        self._dataModel = dataModel
        self._hRules = hRules
        self._pane = None

    def takeControl(self, viewPane: LogMessageViewDialog):
        viewPane._copyButton.clicked.connect(self.copyButtonClicked)
        self._pane = viewPane

    def _highlightingData(self, row: int) -> HighlightingData:
        return self._dataModel.item(row, Column.logMessage).data(Qt.UserRole)

    def showContentFor(self, row: int, highlightingEnabled: bool):
        tagName = self._dataModel.item(row, Column.tagName).text()
        logLevel = self._dataModel.item(row, Column.logLevel).text()
        logMessage = self._dataModel.item(row, Column.logMessage).text()
        hData = self._highlightingData(row)

        self.setTag(tagName)
        self.setLogLevel(logLevel)
        self.setLogMessage(logMessage)
        self.setStyleSheetAuto(logLevel)
        if highlightingEnabled:
            self.applyHighlighting(hData.items)
        self._pane.exec_()

    def copyButtonClickedEnd(self, oldText: str):
        self._pane._copyButton.setEnabled(True)
        self._pane._copyButton.setText(oldText)

    def copyButtonClicked(self):
        self._pane._copyButton.setEnabled(False)
        oldText = self._pane._copyButton.text()
        self._pane._copyButton.setText("Copied")

        clip = QGuiApplication.clipboard()
        clip.setText(self._pane._logMsgTextBrowser.toPlainText())
        QTimer.singleShot(3000, lambda: self.copyButtonClickedEnd(oldText))

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self._pane._logMsgTextBrowser.document())
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self._pane._logMsgTextBrowser.document())
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: PatternSearchResult, charFormat: QTextCharFormat):
        if keyword.name == "GenericUrl":
            charFormat.setAnchor(True)
            text = self._pane._logMsgTextBrowser.document().toPlainText()
            addr = text[keyword.begin : keyword.end]
            charFormat.setAnchorHref(addr)
            charFormat.setToolTip(addr)

        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)

    def setFontForContent(self, font: QFont):
        self._pane._logMsgTextBrowser.document().setDefaultFont(font)

    def setTag(self, tag: str):
        self._pane._tagNameLabel.setText(f"Tag: {tag}")

    def setLogLevel(self, logLevel: str):
        if logLevel == "S":
            desc = "Silent"
        elif logLevel == "F":
            desc = "Fatal"
        elif logLevel == "E":
            desc = "Error"
        elif logLevel == "I":
            desc = "Info"
        elif logLevel == "W":
            desc = "Warning"
        elif logLevel == "D":
            desc = "Debug"
        elif logLevel == "V":
            desc = "Verbose"
        else:
            desc = "<Unknown level>"

        self._pane._logLevelLabel.setText(f"Log level: {desc}")

    def setLogMessage(self, msg: str):
        self._pane._logMsgTextBrowser.setPlainText(msg)

    def setStyleSheetAuto(self, logLevel: str):
        color = logLevelColor(logLevel).name(QColor.HexRgb)
        colorDarker = logLevelColorDarker(logLevel).name(QColor.HexRgb)

        assert self.QSS_TEMPLATE is not None
        styleSheet = deepcopy(self.QSS_TEMPLATE)
        styleSheet = styleSheet.replace("$color_normal$", color)
        styleSheet = styleSheet.replace("$color_darker$", colorDarker)
        self._pane.setStyleSheet(styleSheet)

    def applyHighlighting(self, items: List[PatternSearchResult]):
        for item in items:
            rule = self._hRules.findRule(item.name)
            groupNum = item.groupNum

            charFormat = rule.match
            if groupNum != 0:
                charFormat = rule.groups[groupNum]

            self.highlightKeyword(item, charFormat)
