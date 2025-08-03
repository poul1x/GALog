import shutil
import logging
import platform
import subprocess
import sys
import tarfile
import traceback
from contextlib import suppress
from typing import List

from PyQt5.QtCore import QEvent, QThread, QThreadPool, QUrl
from PyQt5.QtGui import QDesktopServices, QFontDatabase, QFont, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QMainWindow,
    QMenu,
    QMenuBar,
    QStyle,
    QStyleOptionButton,
    QWidgetAction,
    QWidget,
)

from galog.app.device import adbClient
from galog.app.hrules import HRulesStorage
from galog.app.logging import initializeLogging
from galog.app.msgbox import msgBoxErr, msgBoxInfo, msgBoxNotImp, msgBoxPrompt
from galog.app.paths import (
    appConfigDir,
    appDataDir,
    appLogsDir,
    appLogsRootDir,
    fontFiles,
    hRulesFiles,
    iconFile,
    loggingConfigFile,
    styleSheetFiles,
)
from galog.app.settings import readSettings, writeSettings
from galog.app.settings.models import RunAppAction, TagFilteringMode
from galog.app.ui.actions.get_app_pids import GetAppPidsAction
from galog.app.ui.actions.restart_app import RestartAppAction
from galog.app.ui.actions.start_app import StartAppAction
from galog.app.ui.actions.stop_app import StopAppAction
from galog.app.ui.base.style import GALogStyle
from galog.app.ui.core.device_select_dialog import DeviceSelectDialog
from galog.app.ui.core.log_messages_panel import LogMessagesPanel

from galog.app.ui.core.package_select_dialog import PackageSelectDialog
from galog.app.ui.core.tag_filter_dialog import TagFilterDialog
from galog.app.ui.quick_dialogs import RestartCaptureDialog
from galog.app.ui.quick_dialogs.stop_capture_dialog import StopCaptureDialog
from galog.app.ui.reusable.file_picker import FileExtensionFilterBuilder, FilePicker
from galog.app.user_data import initializeUserData

class GALogMenuBar(QMenuBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._checkEmojiFontSupport()

    @staticmethod
    def _preferredEmojiFontFamily():
        system = platform.system()
        if system == "Windows":
            return "Segoe UI Emoji"
        elif system == "Linux":
            return "Emoji One"
        elif system == "Darwin":
            return "Apple Color Emoji"
        else:
            return None

    def _checkEmojiFontSupport(self):
        self._hasEmojiFont = False
        emojiFontFamily = self._preferredEmojiFontFamily()
        if emojiFontFamily in QFontDatabase().families():
            emojiFont = QFont(emojiFontFamily)
            self.setFont(emojiFont)
            self._hasEmojiFont = True

    def addCaptureMenu(self):
        if self._hasEmojiFont:
            return self.addMenu("📱 &Capture")
        else:
            return self.addMenu("&Capture")

    def addOptionsMenu(self):
        if self._hasEmojiFont:
            return self.addMenu("🛠 &Options")
        else:
            return self.addMenu("&Options")
