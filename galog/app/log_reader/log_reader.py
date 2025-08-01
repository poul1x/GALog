from typing import List

from PyQt5.QtCore import QObject, pyqtSignal

from galog.app.device import AdbClient

from .log_reader_thread import LogcatReaderThread
from .models import LogLine, ProcessEndedEvent, ProcessStartedEvent


class LogReaderSignals(QObject):
    failed = pyqtSignal(str, str)
    lineRead = pyqtSignal(LogLine)
    processStarted = pyqtSignal(ProcessStartedEvent)
    processEnded = pyqtSignal(ProcessEndedEvent)
    appStarted = pyqtSignal(str)
    appEnded = pyqtSignal(str)


class AndroidAppLogReader:
    def __init__(self, client: AdbClient, device: str, package: str, pids: List[str]):
        super().__init__()
        self._client = client
        self._deviceName = device
        self._packageName = package
        self._readerThread = LogcatReaderThread(client, device)
        self._pids = set(pids)

        self.signals = LogReaderSignals()
        self._readerThread.lineRead.connect(self.onLineRead)
        self._readerThread.processStarted.connect(self.onProcessStarted)
        self._readerThread.processEnded.connect(self.onProcessEnded)
        self._readerThread.failed.connect(self.onFailed)

    @property
    def device(self):
        return self._deviceName

    @property
    def package(self):
        return self._packageName

    def onLineRead(self, line: LogLine):
        if line.pid in self._pids:
            self.signals.lineRead.emit(line)

    def onProcessStarted(self, event: ProcessStartedEvent):
        if event.packageName == self._packageName:
            if not self._pids:
                self.signals.appStarted.emit(event.packageName)
            self._pids.add(event.processId)
            self.signals.processStarted.emit(event)

    def onProcessEnded(self, event: ProcessEndedEvent):
        if event.packageName == self._packageName:
            self._pids.discard(event.processId)
            self.signals.processEnded.emit(event)
            if not self._pids:
                self.signals.appEnded.emit(event.packageName)

    def onFailed(self, msgBrief: str, msgVerbose: str):
        self.signals.failed.emit(msgBrief, msgVerbose)

    def start(self):
        self._readerThread.start()

    def stop(self):
        if self._readerThread.isRunning():
            self._readerThread.stop()
            self._readerThread.wait()

    def isRunning(self):
        return self._readerThread.isRunning()
