from abc import ABCMeta, abstractmethod

from ppadb import ClearError, InstallError  # noqa


class DeviceError(Exception, metaclass=ABCMeta):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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
        return "Connection failure"

    @property
    def msgVerbose(self):
        return "Failed to connect to the adb server. Is adb server running?"


class NoDevicesFound(DeviceError):
    @property
    def msgBrief(self):
        return "No connected devices"

    @property
    def msgVerbose(self):
        return "No connected devices found. Please, connect your device to the PC via USB cable"


class DeviceNotFound(DeviceError):
    @property
    def msgBrief(self):
        return "Device is not available"

    @property
    def msgVerbose(self):
        return "Device is no longer available. Please, reconnect it to the PC"


class DeviceStateUnauthorized(DeviceError):
    @property
    def msgBrief(self):
        return "Device is unauthorized"

    @property
    def msgVerbose(self):
        return "Please, allow USB debugging on your device after connecting it to PC"


class DeviceStateInvalid(DeviceError):
    def __init__(self, deviceState: str):
        super().__init__(deviceState)

    @property
    def deviceState(self):
        return self.args[0]

    @property
    def msgBrief(self):
        return "Device error"

    @property
    def msgVerbose(self):
        return self._safeFormatting(
            "Unable to work with device in state '{}'",
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
        return "Device error"

    @property
    def msgVerbose(self):
        return "Unhandled error occurred. Please, enable logging for details"

    def __str__(self) -> str:
        return f"{self.msgBrief}. Reason - {self.reason}"
