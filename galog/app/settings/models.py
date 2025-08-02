from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from typing import List, Optional, Union

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    conint,
    constr,
    model_validator,
)
from pydantic.types import Annotated, StringConstraints
from typing_extensions import Literal

from ipaddress import IPv4Address
import os

from enum import Enum, auto


class RunAppAction(int, Enum):
    StartApp = 0
    StartAppDebug = auto()
    DoNotStartApp = auto()


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
Port = Annotated[int, Field(gt=0, lt=65536)]
FontSize = Annotated[int, Field(ge=8, le=20)]


class RunAppAction(int, Enum):
    StartApp = 0
    StartAppDebug = auto()
    DoNotStartApp = auto()


class AdbServerSettings(BaseModel):
    ipAddr: IPv4Address
    port: Port


class LastSelectedDevice(BaseModel):
    serial: NonEmptyStr
    displayName: NonEmptyStr


class LastSelectedPackage(BaseModel):
    name: NonEmptyStr
    action: RunAppAction


class TagFilteringMode(int, Enum):
    Disabled = 0
    ShowMatching = auto()
    HideMatching = auto()


class TagFilteringSettings(BaseModel):
    mode: TagFilteringMode
    tags: List[str]

    def default(self):
        return TagFilteringSettings(
            mode=TagFilteringMode.Disabled,
            tags=[],
        )


class FontSettings(BaseModel):
    family: NonEmptyStr
    size: FontSize


class AppFontsSettings(BaseModel):
    emoji: Optional[FontSettings] = None
    logViewer: FontSettings
    Standard: FontSettings
    Upsized: FontSettings


class AppSettings(BaseModel):
    adb: AdbServerSettings
    lastSelectedDevice: Optional[LastSelectedDevice] = None
    lastSelectedPackage: Optional[LastSelectedPackage] = None
    advancedTagFilter: Optional[TagFilteringSettings] = None
    lastUsedDirPath: str = ""
    fonts: AppFontsSettings
