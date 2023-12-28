from dataclasses import dataclass
from typing import Optional

import yaml

from galog.app.util.paths import stringsFile


@dataclass
class DeviceError:
    msgBrief: str
    msgVerbose: str


@dataclass
class DeviceErrors:
    connectionError: DeviceError
    noDevicesFound: DeviceError
    deviceNotFound: DeviceError
    deviceStateUnauthorized: DeviceError
    deviceStateInvalid: DeviceError
    runtimeError: DeviceError


@dataclass
class AppStrings:
    deviceErrors: DeviceErrors


_APP_STRINGS: Optional[AppStrings] = None


def appStrings() -> AppStrings:
    assert _APP_STRINGS is not None
    return _APP_STRINGS


def appStringsInit(lang: str):
    global _APP_STRINGS

    filepath = stringsFile(lang)
    with open(filepath, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)

    _APP_STRINGS = AppStrings(
        deviceErrors=DeviceErrors(
            connectionError=DeviceError(
                msgBrief=d["deviceErrors"]["connectionError"]["brief"],
                msgVerbose=d["deviceErrors"]["connectionError"]["verbose"],
            ),
            noDevicesFound=DeviceError(
                msgBrief=d["deviceErrors"]["noDevicesFound"]["brief"],
                msgVerbose=d["deviceErrors"]["noDevicesFound"]["verbose"],
            ),
            deviceNotFound=DeviceError(
                msgBrief=d["deviceErrors"]["deviceNotFound"]["brief"],
                msgVerbose=d["deviceErrors"]["deviceNotFound"]["verbose"],
            ),
            deviceStateUnauthorized=DeviceError(
                msgBrief=d["deviceErrors"]["deviceStateUnauthorized"]["brief"],
                msgVerbose=d["deviceErrors"]["deviceStateUnauthorized"]["verbose"],
            ),
            deviceStateInvalid=DeviceError(
                msgBrief=d["deviceErrors"]["deviceStateInvalid"]["brief"],
                msgVerbose=d["deviceErrors"]["deviceStateInvalid"]["verbose"],
            ),
            runtimeError=DeviceError(
                msgBrief=d["deviceErrors"]["runtimeError"]["brief"],
                msgVerbose=d["deviceErrors"]["runtimeError"]["verbose"],
            ),
        )
    )
