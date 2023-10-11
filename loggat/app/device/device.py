from contextlib import contextmanager
from typing import List, Optional
from ppadb.client import Client
from ppadb.device import Device

from .errors import (
    AdbConnectionError,
    DeviceNotFound,
    DeviceRuntimeError,
    DeviceStateInvalid,
    NoDevicesFound,
)

DEVICE_STATE_OK = "device"


class AdbDevice(Device):
    def __init__(self, client, serial, state):
        super().__init__(client, serial)
        self.state = state


class AdbClient(Client):
    def devices(self, state=None):
        cmd = "host:devices"
        result: str = self._execute_cmd(cmd)

        devices = []
        for line in result.split("\n"):
            if not line:
                break
            try:
                serial, state_ = line.split()
            except ValueError:
                raise RuntimeError("Adb response parse error")

            if state and state != state_:
                continue

            devices.append(AdbDevice(self, serial, state_))

        return devices

    @contextmanager
    def deviceRestricted(self, deviceName: str):
        try:
            device: AdbDevice = self.device(deviceName)
        except RuntimeError:
            raise AdbConnectionError()

        if device is None:
            raise DeviceNotFound()

        if device.state != DEVICE_STATE_OK:
            raise DeviceStateInvalid(device.serial, device.state)

        try:
            yield device
        except RuntimeError as e:
            raise DeviceRuntimeError(device.serial, e)

    def devicesRestricted(self):
        try:
            devices: List[AdbDevice] = self.devices()
        except RuntimeError:
            raise AdbConnectionError()

        if len(devices) == 0:
            raise NoDevicesFound()

        return devices