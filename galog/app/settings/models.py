from enum import Enum, auto
from ipaddress import IPv4Address
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.types import Annotated, StringConstraints

from .constants import MAX_FONT_SIZE, MAX_PORT_LT, MIN_FONT_SIZE, MIN_PORT_GT


class TagFilteringMode(int, Enum):
    Disabled = 0
    ShowMatching = auto()
    HideMatching = auto()


# def validateDirPath(value: str):
#     if not os.path.isabs(value):
#         raise ValueError("Not an absolute file path")

#     if not os.path.isdir(value):
#         raise ValueError("Not a directory")

#     return value


# def validateFilePath(value: str):
#     if not os.path.isabs(value):
#         raise ValueError("Not an absolute file path")

#     if not os.path.isfile(value):
#         raise ValueError("Not a regular file")

#     return value


# DirPath = Annotated[str, AfterValidator(validateDirPath)]
# FilePath = Annotated[str, AfterValidator(validateFilePath)]


NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
Port = Annotated[int, Field(gt=MIN_PORT_GT, lt=MAX_PORT_LT)]
FontSize = Annotated[int, Field(ge=MIN_FONT_SIZE, le=MAX_FONT_SIZE)]


class RunAppAction(int, Enum):
    StartApp = 0
    StartAppDebug = auto()
    DoNotStartApp = auto()


class AdbServerSettings(BaseModel):
    ipAddr: IPv4Address
    port: Port

    @staticmethod
    def new(ipAddr: IPv4Address, port: Port):
        return AdbServerSettings(ipAddr=ipAddr, port=port)


class LastSelectedDevice(BaseModel):
    serial: NonEmptyStr
    displayName: NonEmptyStr

    @staticmethod
    def new(serial: NonEmptyStr, displayName: NonEmptyStr):
        return LastSelectedDevice(serial=serial, displayName=displayName)


class LastSelectedPackage(BaseModel):
    name: NonEmptyStr
    action: RunAppAction

    @staticmethod
    def new(name: NonEmptyStr, action: RunAppAction):
        return LastSelectedPackage(name=name, action=action)


class TagFilteringMode(int, Enum):
    Disabled = 0
    ShowMatching = auto()
    HideMatching = auto()


class AdvancedFilterSettings(BaseModel):
    mode: TagFilteringMode
    tags: List[NonEmptyStr]

    @staticmethod
    def default():
        return AdvancedFilterSettings(
            mode=TagFilteringMode.Disabled,
            tags=[],
        )

    @staticmethod
    def new(mode: TagFilteringMode, tags: List[NonEmptyStr]):
        return AdvancedFilterSettings(mode=mode, tags=tags)


class FontSettings(BaseModel):
    family: NonEmptyStr
    size: FontSize

    @staticmethod
    def new(family: NonEmptyStr, size: FontSize):
        return FontSettings(family=family, size=size)


class AppFontsSettings(BaseModel):
    monospaced: FontSettings
    standard: FontSettings
    upsized: FontSettings
    emoji: Optional[FontSettings] = None
    emojiAddSpace: bool
    emojiEnabled: bool


class LogViewerSettings(BaseModel):
    liveReload: bool
    textHighlighting: bool
    showLineNumbers: bool


class AppSettings(BaseModel):
    adbServer: AdbServerSettings
    lastSelectedDevice: Optional[LastSelectedDevice] = None
    lastSelectedPackage: Optional[LastSelectedPackage] = None
    advancedFilter: Optional[AdvancedFilterSettings] = None
    lastUsedDirPath: str = ""
    fonts: AppFontsSettings
    logViewer: LogViewerSettings
