from contextlib import suppress
from dataclasses import dataclass
import re

from time import sleep
from typing import Callable, List, Optional, Tuple
from ppadb.client import Client
from ppadb.device import Device
from ppadb.connection import Connection
import socket


from PyQt5.QtCore import *
from loggat.app.device import AdbClient, deviceRestricted
from loggat.app.device.device import AdbDevice
from loggat.app.device.errors import DeviceError, AdbConnectionError

from loggat.app.util.event import Event


@dataclass
class LogLine:
    level: str
    tag: str
    pid: str
    msg: str


@dataclass
class ProcessStartedEvent:
    processId: str
    packageName: str
    target: Optional[str]


@dataclass
class ProcessEndedEvent:
    processId: str
    packageName: str


IDLE_INTERVAL_MS = 100
RECV_CHUNK_SIZE = 4096
LOGCAT_CMD = "logcat -v brief -T 1"
# LOGCAT_CMD = "logcat -v brief --pid 20715"


# fmt: off
LOG_LINE = re.compile(r"^([A-Z])/(.+)\( *(\d+)\): (.*)$")
PID_START = re.compile(r"^Start proc ([a-zA-Z0-9._:]+) for ([a-z]+ [^:]+): pid=(\d+) uid=\d+ gids=.*$")
PID_START_5_1 = re.compile(r"^Start proc (\d+):([a-zA-Z0-9._:]+)/[a-z0-9]+ for (.*)$")
PID_START_DALVIK = re.compile(r"^E/dalvikvm\(\s*(\d+)\): >>>>> ([a-zA-Z0-9._:]+) \[ userId:0 \| appId:\d+ \]$")
PID_KILL = re.compile(r"^Killing (\d+):([a-zA-Z0-9._:]+)/[^:]+: (.*)$")
PID_LEAVE = re.compile(r"^No longer want ([a-zA-Z0-9._:]+) \(pid (\d+)\): .*$")
PID_DEATH = re.compile(r"^Process ([a-zA-Z0-9._:]+) \(pid (\d+)\) has died.?$")
# fmt: on


class LogLineReader:
    _buf: bytes

    def __init__(self) -> None:
        self._buf = bytes()

    def addDataChunk(self, chunk: bytes):
        self._buf += chunk

    def readParsedLines(self):
        lines = self._buf.split(b"\n")
        self._buf = lines.pop()

        for line in lines:
            decodedLine = line.decode("utf-8", errors="replace")
            match: re.Match = LOG_LINE.match(decodedLine)
            if not match:
                continue

            groups: Tuple[str] = match.groups()
            yield LogLine(
                level=groups[0],
                tag=groups[1].strip(),
                pid=groups[2].strip(),
                msg=groups[3],
            )


class LogcatReaderThread(QThread):
    failed = pyqtSignal(str, str)
    lineRead = pyqtSignal(LogLine)
    processStarted = pyqtSignal(ProcessStartedEvent)
    processEnded = pyqtSignal(ProcessEndedEvent)

    def __init__(self, client: AdbClient, device: str) -> None:
        super().__init__()
        self._client = client
        self._deviceName = device
        self._stopEvent = Event()

    def _parseProcessStart(self, line: LogLine):
        match: re.Match = PID_START_5_1.match(line.msg)
        if match is not None:
            return ProcessStartedEvent(
                processId=match.group(1),
                packageName=match.group(2),
                target=match.group(3),
            )

        match: re.Match = PID_START.match(line.msg)
        if match is not None:
            return ProcessStartedEvent(
                processId=match.group(3),
                packageName=match.group(1),
                target=match.group(2),
            )

        match: re.Match = PID_START_DALVIK.match(line.msg)
        if match is not None:
            return ProcessStartedEvent(
                processId=match.group(1),
                packageName=match.group(2),
                target=None,
            )

        return None

    def _parseProcessEnd(self, line: LogLine):
        if line.tag != "ActivityManager":
            return None

        match: re.Match = PID_KILL.match(line.msg)
        if match is not None:
            return ProcessEndedEvent(
                processId=match.group(1),
                packageName=match.group(2),
            )

        match: re.Match = PID_LEAVE.match(line.msg)
        if match is not None:
            return ProcessEndedEvent(
                processId=match.group(2),
                packageName=match.group(1),
            )

        match: re.Match = PID_DEATH.match(line.msg)
        if match is not None:
            return ProcessEndedEvent(
                processId=match.group(2),
                packageName=match.group(1),
            )

        return None

    def _processLine(self, line: LogLine):
        processStart = self._parseProcessStart(line)
        if processStart is not None:
            self.processStarted.emit(processStart)
            return

        processEnd = self._parseProcessEnd(line)
        if processEnd is not None:
            self.processEnded.emit(processEnd)
            return

        self.lineRead.emit(line)

    def _liveLogRead(self, device: AdbDevice):
        reader = LogLineReader()
        conn: Connection = device.create_connection()
        conn.send("shell:{}".format(LOGCAT_CMD))
        conn.socket.setblocking(False)

        while True:
            with suppress(BlockingIOError):
                data = conn.read(RECV_CHUNK_SIZE)
                if not data:
                    raise AdbConnectionError()

                reader.addDataChunk(data)
                for line in reader.readParsedLines():
                    self._processLine(line)
                    QThread.msleep(10)  # Use delay to avoid UI freezing

            self._stopEvent.wait(IDLE_INTERVAL_MS)
            if self._stopEvent.isSet():
                break

    def run(self):
        try:
            with deviceRestricted(self._client, self._deviceName) as device:
                self._liveLogRead(device)

        except DeviceError as e:
            self.failed.emit(e.msgBrief, e.msgVerbose)

    def stop(self):
        self._stopEvent.set()


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
        self._pids = set()

        self.signals = LogReaderSignals()
        self._readerThread.lineRead.connect(self.onLineRead)
        self._readerThread.processStarted.connect(self.onProcessStarted)
        self._readerThread.processEnded.connect(self.onProcessEnded)
        self._readerThread.failed.connect(self.onFailed)

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
            with deviceRestricted(self._client, self._deviceName) as device:
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
