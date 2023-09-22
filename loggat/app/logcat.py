from contextlib import suppress
from dataclasses import dataclass
from time import sleep
from typing import Callable, List, Optional
from ppadb.client import Client
from ppadb.device import Device
from ppadb.connection import Connection
from threading import Thread, Event
from .util.event import Event
import socket


from PyQt5.QtCore import *

@dataclass
class LogcatLine:
    level: str
    tag: str
    msg: str


IDLE_INTERVAL_MS = 100
RECV_CHUNK_SIZE = 4096
LOGCAT_CMD = "logcat -v tag"


class LogcatLineReader:
    _buf: bytes

    def __init__(self) -> None:
        self._buf = bytes()

    def addDataChunk(self, chunk: bytes):
        self._buf += chunk

    def _parseLine(self, line: bytes):
        decodedLine = line.decode("utf-8", errors="replace")
        fmt, msg = decodedLine.split(":", 1)
        level, tag = fmt.split("/")
        return LogcatLine(level, tag, msg)

    def readParsedLines(self):
        lines = self._buf.split(b"\n")
        self.buf = lines.pop()

        result = []
        for line in lines:
            try:
                result.append(self._parseLine(line))
            except Exception:
                # print(f"Failed to parse line: {line}")
                pass

        return result

class LogcatReaderThread(QThread):

    lineRead = pyqtSignal(LogcatLine)

    def __init__(self, device: Device) -> None:
        super().__init__()
        self._device = device
        self._stopEvent = Event()

    def run(self):
        reader = LogcatLineReader()
        conn: Connection = self._device.create_connection()
        conn.send("shell:{}".format(LOGCAT_CMD))
        conn.socket.setblocking(False)

        while True:
            with suppress(BlockingIOError):
                data = conn.read(RECV_CHUNK_SIZE)
                if not data:
                    break

                reader.addDataChunk(data)
                for line in reader.readParsedLines():
                    self.lineRead.emit(line)
                    sleep(0.0005) # Use delay to avoid UI freezing

            self._stopEvent.wait(IDLE_INTERVAL_MS)
            if self._stopEvent.isSet():
                break



    def stop(self):
        self._stopEvent.set()

class AndroidLogReader:

    def __init__(self, host: str, port: str, serial: str):
        try:
            device = Client(host, port).device(serial)
            if device is None:
                raise Exception("No such device")
        except Exception:
            raise

        self._readerThread = LogcatReaderThread(device)
        self.lineRead = self._readerThread.lineRead

    def start(self):
        self._readerThread.start()

    def stop(self):
        self._readerThread.stop()
        self._readerThread.wait()