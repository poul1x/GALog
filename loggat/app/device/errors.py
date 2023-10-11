from enum import Enum, auto


class ErrorType(int, Enum):
    ConnectionFailure = auto()
    NoDevicesFound = auto()
    DeviceNotFound = auto()
    DeviceStateInvalid = auto()
    RuntimeError = auto()


class DeviceError(Exception):
    def __init__(self, errorType: ErrorType, *args):
        super().__init__(errorType, *args)

    @property
    def errorType(self):
        return self.args[0]


class AdbConnectionError(DeviceError):
    def __init__(self):
        super().__init__(ErrorType.ConnectionFailure)


class NoDevicesFound(DeviceError):
    def __init__(self):
        super().__init__(ErrorType.NoDevicesFound)


class DeviceStateInvalid(DeviceError):
    def __init__(self, deviceName: str, deviceState: str):
        super().__init__(ErrorType.DeviceStateInvalid, deviceName, deviceState)

    @property
    def deviceName(self):
        return self.args[1]

    @property
    def deviceState(self):
        return self.args[2]


class DeviceNotFound(DeviceError):
    def __init__(self, deviceName: str):
        super().__init__(ErrorType.DeviceNotFound, deviceName)

    @property
    def deviceName(self):
        return self.args[1]


class DeviceRuntimeError(DeviceError):
    def __init__(self, deviceName: str, reason: str):
        super().__init__(ErrorType.RuntimeError, deviceName, reason)

    @property
    def deviceName(self):
        return self.args[1]

    @property
    def reason(self):
        return self.args[2]
