from contextlib import suppress
from dataclasses import dataclass
from typing import Optional, Tuple

from ppadb.connection import Connection
from PyQt5.QtCore import QObject, QThread, QThreadPool, pyqtSignal

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.device import AdbDevice
from galog.app.device.errors import DeviceError
from .event import Event
from .models import LogLine, ProcessEndedEvent, ProcessStartedEvent
from .log_reader_thread import LogcatReaderThread
import re

class LogReaderSignals(QObject):
    failed = pyqtSignal(str, str)
    lineRead = pyqtSignal(LogLine)
    processStarted = pyqtSignal(ProcessStartedEvent)
    processEnded = pyqtSignal(ProcessEndedEvent)
    initialized = pyqtSignal(str, str, list)
    appStarted = pyqtSignal(str)
    appEnded = pyqtSignal(str)


class AndroidAppLogReader:
    def __init__(self, client: AdbClient, device: str, package: str):
        super().__init__()
        self._client = client
        self._deviceName = device
        self._packageName = package
        self._readerThread = LogcatReaderThread(client, device)
        self._startDelay = 0
        self._pids = set()

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

    def setStartDelay(self, startDelay: str):
        self._startDelay = startDelay

    def _delayIfNeeded(self):
        if self._startDelay:
            QThread.msleep(self._startDelay)

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

    def _getAppPidsAndStartReaderThread(self):
        try:
            self._delayIfNeeded()
            with deviceRestricted(self._deviceName, self._client) as device:
                output: str = device.shell(f"pidof {self._packageName}")
                self._pids = set(output.split())

        except DeviceError as e:
            self.signals.failed.emit(e.msgBrief, e.msgVerbose)
            return

        self.signals.initialized.emit(
            self._deviceName,
            self._packageName,
            list(self._pids),
        )
        self._readerThread.start()

    def start(self):
        QThreadPool.globalInstance().start(
            self._getAppPidsAndStartReaderThread,
        )

    def stop(self):
        if self._readerThread.isRunning():
            self._readerThread.stop()
            self._readerThread.wait()

    def isRunning(self):
        return self._readerThread.isRunning()
