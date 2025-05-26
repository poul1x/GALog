
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogLine:
    tag: str
    level: str
    msg: str
    pid: str


@dataclass
class ProcessStartedEvent:
    processId: str
    packageName: str
    target: Optional[str]


@dataclass
class ProcessEndedEvent:
    processId: str
    packageName: str
