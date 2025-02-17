from abc import abstractmethod
from PyQt5.QtCore import QRunnable, QThread
import logging

class BackgroundTask(QRunnable):
    def __init__(self):
        super().__init__()
        self._msDelay = -1

    def setStartDelay(self, msDelay: int):
        assert msDelay > 0, "Delay must be greater than 0"
        self._msDelay = msDelay

    def delayIfNeeded(self):
        if self._msDelay == -1:
            return

        logging.debug(f"Sleep {self._msDelay}ms")
        QThread.msleep(self._msDelay)

    @abstractmethod
    def entrypoint(self):
        pass

    def run(self):
        try:
            self.delayIfNeeded()
            self.entrypoint()

        except:
            logging.exception("BG Task Entrypoint")