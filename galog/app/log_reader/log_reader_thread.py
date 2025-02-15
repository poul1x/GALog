from contextlib import suppress
from dataclasses import dataclass
from typing import Optional, Tuple

from ppadb.connection import Connection
from PyQt5.QtCore import QObject, QThread, QThreadPool, pyqtSignal

from galog.app.device import AdbClient, deviceRestricted
from galog.app.device.device import AdbDevice
from galog.app.device.errors import DeviceError
from .event import Event
from .models import LogLine, ProcessStartedEvent, ProcessEndedEvent
import re

IDLE_INTERVAL_MS = 100
RECV_CHUNK_SIZE = 4096
LOGCAT_CMD = "logcat -v brief -T 1"

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
                    msgBrief = "Connection error"
                    msgVerbose = "Failed to read data"
                    self.failed.emit(msgBrief, msgVerbose)
                    break

                reader.addDataChunk(data)
                for line in reader.readParsedLines():
                    self._processLine(line)

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