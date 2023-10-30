from abc import abstractmethod, ABCMeta
from enum import Enum, auto
from galog.app.app_strings import appStrings


class DeviceError(Exception, metaclass=ABCMeta):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self._strings = appStrings()

    @property
    @abstractmethod
    def msgBrief(self):
        pass

    @property
    @abstractmethod
    def msgVerbose(self):
        pass

    def _safeFormatting(self, fmt: str, *args: str):
        try:
            res = fmt.format(*args)
        except IndexError:
            res = fmt

        return res

    def __str__(self) -> str:
        return f"{self.msgBrief}. {self.msgVerbose}"


class AdbConnectionError(DeviceError):
    @property
    def msgBrief(self):
        return self._strings.deviceErrors.connectionError.msgBrief

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.connectionError.msgVerbose


class NoDevicesFound(DeviceError):
    @property
    def msgBrief(self):
        return self._strings.deviceErrors.noDevicesFound.msgBrief

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.noDevicesFound.msgVerbose


class DeviceNotFound(DeviceError):
    def __init__(self, deviceName: str):
        super().__init__(deviceName)

    @property
    def deviceName(self):
        return self.args[0]

    @property
    def msgBrief(self):
        return self._safeFormatting(
            self._strings.deviceErrors.deviceNotFound.msgBrief,
            self.deviceName,
        )

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.deviceNotFound.msgVerbose

class DeviceStateUnauthorized(DeviceError):
    def __init__(self, deviceName: str):
        super().__init__(deviceName)

    @property
    def deviceName(self):
        return self.args[0]

    @property
    def msgBrief(self):
        return self._safeFormatting(
            self._strings.deviceErrors.deviceStateUnauthorized.msgBrief,
            self.deviceName,
        )

    @property
    def msgVerbose(self):
        self._strings.deviceErrors.deviceStateUnauthorized.msgVerbose,


class DeviceStateInvalid(DeviceError):
    def __init__(self, deviceName: str, deviceState: str):
        super().__init__(deviceName, deviceState)

    @property
    def deviceName(self):
        return self.args[0]

    @property
    def deviceState(self):
        return self.args[1]

    @property
    def msgBrief(self):
        return self._safeFormatting(
            self._strings.deviceErrors.deviceStateInvalid.msgBrief,
            self.deviceName,
        )

    @property
    def msgVerbose(self):
        return self._safeFormatting(
            self._strings.deviceErrors.deviceStateInvalid.msgVerbose,
            self.deviceState,
        )


class DeviceRuntimeError(DeviceError):
    def __init__(self, deviceName: str, reason: str):
        super().__init__(deviceName, reason)

    @property
    def deviceName(self):
        return self.args[0]

    @property
    def reason(self):
        return self.args[1]

    @property
    def msgBrief(self):
        return self._safeFormatting(
            self._strings.deviceErrors.runtimeError.msgBrief,
            self.deviceName,
        )

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.runtimeError.msgVerbose

    def __str__(self) -> str:
        return f"{self.msgBrief}. Reason - {self.reason}"
