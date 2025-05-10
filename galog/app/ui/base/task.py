from abc import abstractmethod
from PyQt5.QtCore import QRunnable, QThread
import logging


class BaseTask(QRunnable):
    def __init__(self):
        super().__init__()
        self._msDelay = -1
        self.initLogger()

    def initLogger(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def setStartDelay(self, msDelay: int):
        assert msDelay > 0, "Delay must be greater than 0"
        self._msDelay = msDelay

    def delayIfNeeded(self):
        if self._msDelay == -1:
            return

        self._logger.debug("Delay for %dms", self._msDelay)
        QThread.msleep(self._msDelay)

    @abstractmethod
    def entrypoint(self):
        pass

    def run(self):
        try:
            self._logger.debug("Delay if needed")
            self.delayIfNeeded()

            self._logger.debug("Call entrypoint")
            self.entrypoint()
            self._logger.debug("Call entrypoint - OK")

        except Exception:
            self._logger.exception("Unhandled exception in task entrypoint:")
