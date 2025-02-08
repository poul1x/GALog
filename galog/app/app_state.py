from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class RunAppAction(int, Enum):
    StartApp = 0
    StartAppDebug = auto()
    DoNotStartApp = auto()


@dataclass
class AdbServerSettings:
    ipAddr: str
    port: int


@dataclass
class LastSelectedDevice:
    serial: str
    displayName: str


@dataclass
class LastSelectedPackage:
    name: str
    action: RunAppAction


@dataclass
class AppState:
    adb: AdbServerSettings
    lastSelectedDevice: Optional[LastSelectedDevice]
    lastSelectedPackage: Optional[LastSelectedPackage]
