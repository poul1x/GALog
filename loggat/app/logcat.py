from dataclasses import dataclass
from typing import Callable, List, Optional
from ppadb.client import Client
from ppadb.device import Device
from ppadb.connection import Connection
from threading import Thread, Event


@dataclass
class LogcatLine:
    level: str
    tag: str
    msg: str


RECV_CHUNK_SIZE = 4096
LOGCAT_CMD = "logcat -v tag"
IDLE_SECONDS = 0.1
LogcatLineCallback = Callable[[LogcatLine], None]


class LogcatLineReader:
    _buf: bytes

    def __init__(self) -> None:
        self._buf = bytes()

    def addDataChunk(self, chunk: bytes):
        self._buf += chunk

    def readParsedLines(self):
        lines = self._buf.split(b"\n")
        self.buf = lines.pop()

        result = []
        for line in lines:
            decodedLine = line.decode("utf-8", errors="replace")
            print(decodedLine)
            fmt, msg = decodedLine.split(":", 1)
            level, tag = fmt.split("/")

            parsedLine = LogcatLine(level, tag, msg)
            result.append(parsedLine)

        return result


class LogcatReaderThread(Thread):
    _stopEvent: Event
    _callback: LogcatLineCallback
    _device: Device

    def __init__(self, device: Device) -> None:
        super().__init__()
        self._device = device
        self._stopEvent = Event()
        self._callback = LogcatReaderThread.defaultCallback

    def defaultCallback(line: LogcatLine):
        fmt = "level='%s', tag='%s', msg='%s'"
        args = line.level, line.tag, line.msg
        print(fmt % args)

    def setOnLineCallback(self, callback: LogcatLineCallback):
        self._callback = callback

    def run(self):
        reader = LogcatLineReader()
        conn: Connection = self._device.create_connection(timeout=None)
        conn.send("shell:{}".format(LOGCAT_CMD))
        conn.read(30) # skip b'--------- beginning of system\n'

        while True:
            reader.addDataChunk(conn.read(RECV_CHUNK_SIZE))
            for line in reader.readParsedLines():
                self._callback(line)

            self._stopEvent.wait(IDLE_SECONDS)
            if self._stopEvent.isSet():
                break

    def stop(self):
        self._stopEvent.set()


_logcatReaderThread: Optional[LogcatReaderThread] = None


def startLogcatReaderThread(deviceName: str, onLine: LogcatLineCallback):
    global _logcatReaderThread
    assert _logcatReaderThread is None
    client = Client(host="127.0.0.1", port=5037)
    device: Device = client.device(deviceName)
    _logcatReaderThread = LogcatReaderThread(device)
    _logcatReaderThread.setOnLineCallback(onLine)
    _logcatReaderThread.start()


def stopLogcatReaderThread():
    global _logcatReaderThread
    if _logcatReaderThread is None:
        return

    _logcatReaderThread.stop()
    _logcatReaderThread.join()
    _logcatReaderThread = None
