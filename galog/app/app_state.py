
from dataclasses import dataclass
from typing import Optional


@dataclass
class AdbServerSettings:
    ipAddr: str
    port: int

@dataclass
class LastSelectedDevice:
    serial: str
    displayName: str

@dataclass
class AppState:
    adb: AdbServerSettings
    lastSelectedDevice: Optional[LastSelectedDevice]
