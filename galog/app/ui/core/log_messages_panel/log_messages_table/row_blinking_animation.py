from PyQt5.QtCore import QObject, QRunnable, Qt, QThread, QThreadPool, pyqtSignal
from PyQt5.QtGui import QStandardItemModel

from .data_model import Column


class BlinkingSignals(QObject):
    finished = pyqtSignal()
    blink = pyqtSignal()


class BlinkingTimerTask(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = BlinkingSignals()
        self._blinkCount = 2
        self._blinkInterval = 50
        self._blinkDuration = 100

    def run(self):
        for _ in range(self._blinkCount):
            self.signals.blink.emit()
            QThread.msleep(self._blinkDuration)
            self.signals.blink.emit()
            QThread.msleep(self._blinkInterval)

        self.signals.finished.emit()

    def setBlinkCount(self, count: int):
        self._blinkCount = count

    def blinkCount(self):
        return self._blinkCount

    def setBlinkDuration(self, duration: int):
        self._blinkDuration = duration

    def blinkDuration(self):
        return self._blinkDuration


class RowBlinkingAnimation(QObject):

    finished = pyqtSignal()

    def __init__(self, row: int, model: QStandardItemModel) -> None:
        super().__init__()
        self._model = model
        self._inverted = False
        self._row = row

    def row(self):
        return self._row

    def _invertColors(self):
        self._inverted = not self._inverted

    def _forceRedrawRow(self):
        self._invertColors()
        for column in Column:
            index = self._model.index(self._row, column)
            self._model.dataChanged.emit(index, index)

    def startBlinking(self):
        worker = BlinkingTimerTask()
        worker.signals.finished.connect(lambda: self.finished.emit())
        worker.signals.blink.connect(self._forceRedrawRow)
        QThreadPool.globalInstance().start(worker)

    def colorInverted(self):
        return self._inverted
