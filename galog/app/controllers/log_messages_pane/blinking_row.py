from PyQt5.QtCore import QObject, QRunnable, Qt, QThread, QThreadPool, pyqtSignal

from galog.app.components.log_messages_pane import LogMessagesPane
from galog.app.components.log_messages_pane.data_model import Columns


class RowBlinkingSignals(QObject):
    finished = pyqtSignal()
    invertColors = pyqtSignal(int)


class RowBlinkingWorker(QRunnable):
    def __init__(self, row: int):
        super().__init__()
        self.signals = RowBlinkingSignals()
        self._blinkCount = 2
        self._blinkInterval = 50
        self._blinkDuration = 100
        self._row = row

    def run(self):
        for _ in range(self._blinkCount):
            self.signals.invertColors.emit(self._row)
            QThread.msleep(self._blinkDuration)
            self.signals.invertColors.emit(self._row)
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


class RowBlinkingController:
    def __init__(self, pane: LogMessagesPane):
        self._pane = pane

    def _finished(self):
        self._pane.tableView.setEnabled(True)
        self._pane.tableView.setFocus()

    def _invertColors(self, row: int):
        model = self._pane.filterModel
        index = model.index(row, Columns.logLevel)
        inverted = model.data(index, Qt.UserRole)
        model.setData(index, not inverted, Qt.UserRole)

        for column in Columns:
            index = model.index(row, column)
            model.dataChanged.emit(index, index)

    def startBlinking(self, row: int):
        worker = RowBlinkingWorker(row)
        worker.signals.finished.connect(self._finished)
        worker.signals.invertColors.connect(self._invertColors)
        QThreadPool.globalInstance().start(worker)
        self._pane.tableView.setEnabled(False)
