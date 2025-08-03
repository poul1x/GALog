import logging
import sys
import traceback
from typing import List

from PyQt5.QtWidgets import QApplication, QMessageBox

from galog.app.logging import initializeLogging
from galog.app.paths import styleSheetFiles
from galog.app.ui.core.main_window import GALogMainWindow
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
