from copy import deepcopy
from typing import Optional

from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QGuiApplication, QIcon, QTextCharFormat, QTextCursor, QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from galog.app.hrules import HRulesStorage
from galog.app.log_reader import LogLine
from galog.app.paths import iconFile, styleSheetFile
from galog.app.settings import readSettings
from galog.app.ui.base.dialog import Dialog

from ..colors import logLevelColor, logLevelColorDarker
from ..data_model import HighlightingData
from ..pattern_search_task import PatternSearchResult


class LogMessageViewDialog(Dialog):
    QSS_TEMPLATE: Optional[str] = None

    @staticmethod
    def _loadStyleSheetTemplate():
        if not LogMessageViewDialog.QSS_TEMPLATE:
            path = styleSheetFile("log_message_view_dialog")
            with open(path, "r", encoding="utf-8") as f:
                LogMessageViewDialog.QSS_TEMPLATE = f.read()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = readSettings()
        self._initUserInterface()
        self._initUserInputHandlers()
        self._loadStyleSheetTemplate()
        self.setWindowTitle("View log message")
        self.setRelativeGeometry(0.8, 0.8, 900, 600)
        self.setFixedMinSize(500, 400)
        self.moveToCenter()

    def _setDefaultFont(self, widget: QWidget):
        family = self._settings.fonts.logViewer.family
        size = self._settings.fonts.logViewer.size
        widget.setFont(QFont(family, size))

    def _initUserInputHandlers(self):
        self._copyButton.clicked.connect(self._copyButtonClicked)

    def _copyButtonClickedEnd(self, oldText: str):
        self._copyButton.setEnabled(True)
        self._copyButton.setText(oldText)

    def _copyButtonClicked(self):
        self._copyButton.setEnabled(False)
        oldText = self._copyButton.text()
        self._copyButton.setText("Copied")

        clip = QGuiApplication.clipboard()
        clip.setText(self._logMsgTextBrowser.toPlainText())
        QTimer.singleShot(1000, lambda: self._copyButtonClickedEnd(oldText))

    def _initUserInterface(self):
        self._logLevelLabel = QLabel()
        self._setDefaultFont(self._logLevelLabel)
        self._logLevelLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._logLevelLabel.setFixedWidth(300)
        self._logLevelLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self._tagNameLabel = QLabel()
        self._setDefaultFont(self._tagNameLabel)
        self._tagNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tagNameLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )

        self._copyButton = QPushButton()
        self._setDefaultFont(self._copyButton)
        self._copyButton.setIcon(QIcon(iconFile("copy")))
        self._copyButton.setText("Copy contents")
        self._copyButton.setFixedWidth(220)
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
        self._setDefaultFont(self._logMsgTextBrowser)
        self._logMsgTextBrowser.setOpenExternalLinks(True)
        self._logMsgTextBrowser.setReadOnly(True)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addWidget(self._logMsgTextBrowser, 1)
        self.setLayout(vBoxLayout)

    def _setTag(self, tag: str):
        self._tagNameLabel.setText(f"Tag: {tag}")

    def _setLogLevel(self, logLevel: str):
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

        self._logLevelLabel.setText(f"Log level: {desc}")

    def _setLogMessage(self, msg: str):
        self._logMsgTextBrowser.setPlainText(msg)

    def _setStyleSheetAuto(self, logLevel: str):
        color = logLevelColor(logLevel).name(QColor.HexRgb)
        colorDarker = logLevelColorDarker(logLevel).name(QColor.HexRgb)

        assert self.QSS_TEMPLATE is not None
        styleSheet = deepcopy(self.QSS_TEMPLATE)
        styleSheet = styleSheet.replace("$color_normal$", color)
        styleSheet = styleSheet.replace("$color_darker$", colorDarker)
        self.setStyleSheet(styleSheet)

    def setLogLine(self, logLine: LogLine):
        self._setTag(logLine.tag)
        self._setLogLevel(logLine.level)
        self._setLogMessage(logLine.msg)
        self._setStyleSheetAuto(logLine.level)

    def setHighlighting(self, hRules: HRulesStorage, hData: HighlightingData):
        for item in hData.items:
            rule = hRules.findRule(item.name)
            groupNum = item.groupNum

            charFormat = rule.match
            if groupNum != 0:
                charFormat = rule.groups[groupNum]

            self._highlightKeyword(item, charFormat)

    def _highlightKeyword(
        self, keyword: PatternSearchResult, charFormat: QTextCharFormat
    ):
        if keyword.name == "GenericUrl":
            charFormat.setAnchor(True)
            text = self._logMsgTextBrowser.document().toPlainText()
            addr = text[keyword.begin : keyword.end]
            charFormat.setAnchorHref(addr)
            charFormat.setToolTip(addr)

        cursor = self._cursorSelect(keyword.begin, keyword.end)
        cursor.setCharFormat(charFormat)

    def _cursorSelect(self, begin: int, end: int):
        cursor = QTextCursor(self._logMsgTextBrowser.document())
        cursor.setPosition(begin, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor
