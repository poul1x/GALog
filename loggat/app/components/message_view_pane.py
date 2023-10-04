from traceback import print_tb
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from dataclasses import dataclass
from typing import List
from enum import Enum
from loggat.app.highlighting_rules import HighlightingRules
from loggat.app.mtsearch import SearchResult

from loggat.app.util.paths import iconFile


class LogMessageViewPane(QDialog):

    def _defaultFlags(self):
        return Qt.Window | Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint

    def __init__(self, parent: QWidget):
        super().__init__(parent, self._defaultFlags())
        self.initUserInterface()

    def highlightAllText(self, charFormat: QTextCharFormat):
        cursor = QTextCursor(self._logMsgTextBrowser.document())
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(charFormat)

    def cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self._logMsgTextBrowser.document())
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor

    def highlightKeyword(self, keyword: SearchResult, charFormat: QTextCharFormat):

        if keyword.name == "genericUrl":
            charFormat.setAnchor(True)
            doc = self._logMsgTextBrowser.document()
            text = doc.toPlainText()
            addr = text[keyword.begin: keyword.end]
            charFormat.setAnchorHref(addr)
            charFormat.setToolTip(addr)

        cursor = self.cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)

    def initUserInterface(self):

        self.setObjectName("logMessageViewPane")

        self._logLevelLabel = QLabel()
        self._logLevelLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._logLevelLabel.setFixedWidth(200)
        self._logLevelLabel.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self._tagNameLabel = QLabel()
        self._tagNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tagNameLabel.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self._copyButton = QPushButton()
        self._copyButton.setIcon(QIcon(iconFile("copy")))
        self._copyButton.setText("Copy contents")
        self._copyButton.setFixedWidth(190)
        self._copyButton.clicked.connect(self.copyButtonClicked)

        self._copyButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._copyButton.setIconSize(QSize(32, 32))

        hLeftBoxLayout = QHBoxLayout()
        hLeftBoxLayout.addWidget(self._logLevelLabel)
        hLeftBoxLayout.addWidget(self._tagNameLabel)
        hLeftBoxLayout.setAlignment(Qt.AlignLeft)

        hRightBoxLayout = QHBoxLayout()
        hRightBoxLayout.addWidget(self._copyButton)
        hRightBoxLayout.setAlignment(Qt.AlignRight)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addLayout(hLeftBoxLayout, 1)
        hBoxLayout.addLayout(hRightBoxLayout)

        self._logMsgTextBrowser = QTextBrowser()
        self._logMsgTextBrowser.setOpenExternalLinks(True)
        self._logMsgTextBrowser.setOpenLinks(True)
        self._logMsgTextBrowser.setReadOnly(True)
        self._logMsgTextBrowser.setFocusPolicy(Qt.NoFocus)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addWidget(self._logMsgTextBrowser, 1)

        self.setLayout(vBoxLayout)

        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.5)
        height = int(screen.height() * 0.5)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def copyButtonClicked(self):
        self._copyButton.setEnabled(False)
        self._copyButton.setText("Copied")
        clip = QGuiApplication.clipboard()
        clip.setText(self._logMsgTextBrowser.toPlainText())
        QTimer.singleShot(3000, self.copyButtonClickedEnd)

    def copyButtonClickedEnd(self):
        self._copyButton.setEnabled(True)
        self._copyButton.setText("Copy contents")

    def setTag(self, tag: str):
        self._tagNameLabel.setText(f"Tag: {tag}")

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
        else:  # V
            desc = "Verbose"

        self._logLevelLabel.setText(f"Log level: {desc}")

    def setLogMessage(self, msg: str):
        self._logMsgTextBrowser.setPlainText(msg)

    def setItemBackgroundColor(self, color: QColor):
        stylesheet = f"background-color: {color.name(QColor.HexArgb)};"
        self._logLevelLabel.setStyleSheet(stylesheet)
        self._tagNameLabel.setStyleSheet(stylesheet)
        self._logMsgTextBrowser.setStyleSheet(stylesheet)

    def applyHighlighting(self, rules: HighlightingRules, items: List[SearchResult]):
        for item in items:
            style = rules.getStyle(item.name)
            self.highlightKeyword(item, style)
