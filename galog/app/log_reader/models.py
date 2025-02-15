
from dataclasses import dataclass
from typing import Optional


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
