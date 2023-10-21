from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import (
    QTextCursor,
    QTextCharFormat,
    QIcon,
    QColor,
)
from PyQt5.QtWidgets import (
    QSizePolicy,
    QLabel,
    QDialog,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTextBrowser,
    QApplication,
)


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.util.paths import iconFile

from loggat.app.controllers.log_messages_pane.search import SearchResult


class LogMessageViewPane(QDialog):
    def _defaultFlags(self):
        return (
            Qt.Window
            | Qt.Dialog
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.initUserInterface()

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self.logMsgTextBrowser.document())
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self.logMsgTextBrowser.document())
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: SearchResult, charFormat: QTextCharFormat):
        if keyword.name == "genericUrl":
            charFormat.setAnchor(True)
            doc = self.logMsgTextBrowser.document()
            text = doc.toPlainText()
            addr = text[keyword.begin : keyword.end]
            charFormat.setAnchorHref(addr)
            charFormat.setToolTip(addr)

        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)

    def initUserInterface(self):
        self.logLevelLabel = QLabel()
        self.logLevelLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logLevelLabel.setFixedWidth(200)
        self.logLevelLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.tagNameLabel = QLabel()
        self.tagNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tagNameLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self.copyButton = QPushButton()
        self.copyButton.setIcon(QIcon(iconFile("copy")))
        self.copyButton.setText("Copy contents")
        self.copyButton.setFixedWidth(190)

        self.copyButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.copyButton.setIconSize(QSize(32, 32))

        hLeftBoxLayout = QHBoxLayout()
        hLeftBoxLayout.addWidget(self.logLevelLabel)
        hLeftBoxLayout.addWidget(self.tagNameLabel)
        hLeftBoxLayout.setAlignment(Qt.AlignLeft)

        hRightBoxLayout = QHBoxLayout()
        hRightBoxLayout.addWidget(self.copyButton)
        hRightBoxLayout.setAlignment(Qt.AlignRight)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addLayout(hLeftBoxLayout, 1)
        hBoxLayout.addLayout(hRightBoxLayout)

        self.logMsgTextBrowser = QTextBrowser()
        self.logMsgTextBrowser.setOpenExternalLinks(True)
        self.logMsgTextBrowser.setOpenLinks(True)
        self.logMsgTextBrowser.setReadOnly(True)
        self.logMsgTextBrowser.setFocusPolicy(Qt.NoFocus)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addWidget(self.logMsgTextBrowser, 1)
        self.setLayout(vBoxLayout)

        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def setTag(self, tag: str):
        self.tagNameLabel.setText(f"Tag: {tag}")

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

        self.logLevelLabel.setText(f"Log level: {desc}")

    def setLogMessage(self, msg: str):
        self.logMsgTextBrowser.setPlainText(msg)

    def setItemBackgroundColor(self, color: QColor):
        stylesheet = f"background-color: {color.name(QColor.HexArgb)};"
        self.logLevelLabel.setStyleSheet(stylesheet)
        self.tagNameLabel.setStyleSheet(stylesheet)
        self.logMsgTextBrowser.setStyleSheet(stylesheet)

    def applyHighlighting(self, rules: HighlightingRules, items: List[SearchResult]):
        for item in items:
            style = rules.getStyle(item.name)
            self.highlightKeyword(item, style)
