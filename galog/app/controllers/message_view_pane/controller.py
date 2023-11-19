from typing import List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from galog.app.components.log_messages_pane.data_model import Columns
from galog.app.components.log_messages_pane.delegate import HighlightingData
from galog.app.components.message_view_pane import LogMessageViewPane
from galog.app.controllers.log_messages_pane.search import SearchResult
from galog.app.highlighting import HighlightingRules
from galog.app.util.colors import logLevelColor


class LogMessageViewPaneController:
    def __init__(self, dataModel: QStandardItemModel, hRules: HighlightingRules):
        self._dataModel = dataModel
        self._hRules = hRules
        self._pane = None

    def takeControl(self, viewPane: LogMessageViewPane):
        viewPane.copyButton.clicked.connect(self.copyButtonClicked)
        self._pane = viewPane

    def _highlightingData(self, row: int) -> HighlightingData:
        return self._dataModel.item(row, Columns.logMessage).data(Qt.UserRole)

    def showContentFor(self, row: int):
        tagName = self._dataModel.item(row, Columns.tagName).text()
        logLevel = self._dataModel.item(row, Columns.logLevel).text()
        logMessage = self._dataModel.item(row, Columns.logMessage).text()
        hData = self._highlightingData(row)

        self.setTag(tagName)
        self.setLogLevel(logLevel)
        self.setLogMessage(logMessage)
        self.setItemBackgroundColor(logLevelColor(logLevel))
        self.applyHighlighting(self._hRules, hData.items)
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

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self._pane.logMsgTextBrowser.document())
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self._pane.logMsgTextBrowser.document())
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: SearchResult, charFormat: QTextCharFormat):
        if keyword.name == "genericUrl":
            charFormat.setAnchor(True)
            text = self._pane.logMsgTextBrowser.document().toPlainText()
            addr = text[keyword.begin : keyword.end]
            charFormat.setAnchorHref(addr)
            charFormat.setToolTip(addr)

        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)

    def setFontForContent(self, font: QFont):
        self._pane.logMsgTextBrowser.document().setDefaultFont(font)

    def setTag(self, tag: str):
        self._pane.tagNameLabel.setText(f"Tag: {tag}")

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

        self._pane.logLevelLabel.setText(f"Log level: {desc}")

    def setLogMessage(self, msg: str):
        self._pane.logMsgTextBrowser.setPlainText(msg)

    def setItemBackgroundColor(self, color: QColor):
        colorName = color.name(QColor.HexArgb)
        colorNameHover = color.lighter().name(QColor.HexArgb)

        stylesheet = f"background: {colorName};"
        self._pane.logLevelLabel.setStyleSheet(stylesheet)
        self._pane.tagNameLabel.setStyleSheet(stylesheet)
        self._pane.logMsgTextBrowser.setStyleSheet(stylesheet)

        stylesheet = r"QPushButton {background: %s;}" % colorName
        stylesheet += r"QPushButton:hover {background: %s;}" % colorNameHover
        self._pane.setStyleSheet(stylesheet)

    def applyHighlighting(self, rules: HighlightingRules, items: List[SearchResult]):
        for item in items:
            rule = rules.findRule(item.name)
            self.highlightKeyword(item, rule.charFormat)
