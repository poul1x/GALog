from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


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


class TagFilteringMode(int, Enum):
    Disabled = 0
    ShowMatching = auto()
    HideMatching = auto()


@dataclass
class TagFilteringConfig:
    mode: TagFilteringMode
    tags: List[str]

    @staticmethod
    def none():
        return TagFilteringConfig(
            mode=TagFilteringMode.Disabled,
            tags=[],
        )


@dataclass
class AppState:
    adb: AdbServerSettings
    lastSelectedDevice: Optional[LastSelectedDevice]
    lastSelectedPackage: Optional[LastSelectedPackage]
    tagFilteringConfig: TagFilteringConfig
