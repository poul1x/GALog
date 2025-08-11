import logging
import sys
import traceback
from typing import List

from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt5.QtGui import QFont

from galog.app.logging import initializeLogging
from galog.app.paths import styleSheetFiles
from galog.app.settings.notifier import ChangedEntry, SettingsChangeNotifier
from galog.app.settings.settings import readSettings
from galog.app.ui.core.main_window import GALogMainWindow
from galog.app.user_data import initializeUserData


class GALogApp(QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        self._reloadSettings()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._subscribeSettingsChangeEvents()
        self._loadStyleSheetFiles()
        self._applyFontSettings()

    def _reloadSettings(self):
        self._settings = readSettings()

    def _applyFontSettings(self):
        standardFont = self._settings.fonts.standard
        font = QFont(standardFont.family, standardFont.size)
        self.setFont(font)

    def _loadStyleSheetFiles(self):
        styleSheet = ""
        for filePath in styleSheetFiles():
            self._logger.info("Load styleSheet from '%s'", filePath)
            with open(filePath, "r", encoding="utf-8") as f:
                styleSheet += f.read() + "\n"

        self.setStyleSheet(styleSheet)

    def _settingsChanged(self, changedEntry: ChangedEntry):
        self._reloadSettings()
        if changedEntry == ChangedEntry.AppFontSettingsStandard:
            self._applyFontSettings()

    def _subscribeSettingsChangeEvents(self):
        notifier = SettingsChangeNotifier()
        notifier.settingsChanged.connect(self._settingsChanged)


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


def runGUIApplication():
    try:
        app = GALogApp(sys.argv)
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
    initializeUserDataOrDie()
    initializeLoggingOrDie()
    sys.exit(runGUIApplication())
