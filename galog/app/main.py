import os
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
    QMessageBox,
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

from galog.app.ui.core.main_window import GALogMainWindow
from galog.app.ui.core.package_select_dialog import PackageSelectDialog
from galog.app.ui.core.tag_filter_dialog import TagFilterDialog
from galog.app.ui.quick_dialogs import RestartCaptureDialog
from galog.app.ui.quick_dialogs.stop_capture_dialog import StopCaptureDialog
from galog.app.ui.reusable.file_picker import FileExtensionFilterBuilder, FilePicker
from galog.app.user_data import initializeUserData


class GALogApp(QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.loadStyleSheetFiles()

    def loadStyleSheetFiles(self):
        styleSheet = ""
        for filePath in styleSheetFiles():
            self._logger.info("Load styleSheet from '%s'", filePath)
            with open(filePath, "r", encoding="utf-8") as f:
                styleSheet += f.read() + "\n"

        self.setStyleSheet(styleSheet)


def runGUIApp(app: GALogApp):
    mainWindow = GALogMainWindow()
    mainWindow.show()
    result = app.exec()

    # Keep this to properly cleanup.
    # Executable, created with PyInstaller,
    # may get SIGSEGV on exit without this
    mainWindow.deleteLater()
    return result


def initializeLoggingOrDie():
    try:
        initializeLogging()
    except Exception:
        title = "GALog - Logging initialization error"
        text = "Failed to initialize logging module. Unable to continue"
        QMessageBox.critical(None, title, text)
        traceback.print_exc()
        sys.exit(1)


def initializeUserDataOrDie():
    try:
        initializeUserData()
    except Exception:
        title = "GALog - Initialization error"
        text = "Failed to initialize user data directories. Unable to continue"
        QMessageBox.critical(None, title, text)
        traceback.print_exc()
        sys.exit(1)


def runGUIApplication(app: GALogApp):
    try:
        mainWindow = GALogMainWindow()
        mainWindow.show()
        result = app.exec()

        # Keep this to properly cleanup.
        # Executable, created with PyInstaller,
        # may get SIGSEGV on exit without this
        mainWindow.deleteLater()

    except Exception:
        title = "GALog - Crashed"
        text = "Unrecorevable application error. GALog will be closed now"
        QMessageBox.critical(None, title, text)
        logging.exception("CRASH")
        return 1

    return result


def runApp():
    app = GALogApp(sys.argv)
    initializeUserDataOrDie()
    initializeLoggingOrDie()
    sys.exit(runGUIApplication(app))
