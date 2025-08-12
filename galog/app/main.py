import logging
import sys
import traceback
from typing import List

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMessageBox

from galog.app.logging import initializeLogging
from galog.app.paths import styleSheetFiles
from galog.app.settings.notifier import ChangedEntry, SettingsChangeNotifier
from galog.app.settings.settings import readSettings
from galog.app.ui.core.main_window import MainWindow
from galog.app.user_data import initializeUserData

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


def runGUIApplication(app: QApplication):
    try:
        mainWindow = MainWindow()
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
    app = QApplication(sys.argv)
    initializeUserDataOrDie()
    initializeLoggingOrDie()
    sys.exit(runGUIApplication(app))
