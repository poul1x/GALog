from abc import ABCMeta, abstractmethod

from ppadb import ClearError, InstallError  # noqa

from galog.app.strings import appStrings


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
    @property
    def msgBrief(self):
        return self._strings.deviceErrors.deviceNotFound.msgBrief

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.deviceNotFound.msgVerbose


class DeviceStateUnauthorized(DeviceError):
    @property
    def msgBrief(self):
        return self._strings.deviceErrors.deviceStateUnauthorized.msgBrief

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.deviceStateUnauthorized.msgVerbose


class DeviceStateInvalid(DeviceError):
    def __init__(self, deviceState: str):
        super().__init__(deviceState)

    @property
    def deviceState(self):
        return self.args[0]

    @property
    def msgBrief(self):
        return self._strings.deviceErrors.deviceStateInvalid.msgBrief

    @property
    def msgVerbose(self):
        return self._safeFormatting(
            self._strings.deviceErrors.deviceStateInvalid.msgVerbose,
            self.deviceState,
        )


class DeviceRuntimeError(DeviceError):
    def __init__(self, reason: str):
        super().__init__(reason)

    @property
    def reason(self):
        return self.args[0]

    @property
    def msgBrief(self):
        return self._strings.deviceErrors.runtimeError.msgBrief

    @property
    def msgVerbose(self):
        return self._strings.deviceErrors.runtimeError.msgVerbose

    def __str__(self) -> str:
        return f"{self.msgBrief}. Reason - {self.reason}"
