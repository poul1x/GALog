from contextlib import contextmanager
from typing import List, Tuple

from ppadb.client import Client
from ppadb.device import Device

from .errors import (
    AdbConnectionError,
    DeviceNotFound,
    DeviceRuntimeError,
    DeviceStateInvalid,
    DeviceStateUnauthorized,
    NoDevicesFound,
)

DEVICE_STATE_OK = "device"
DEVICE_STATE_UNAUTHORIZED = "unauthorized"


# Use this as alias
# https://github.com/microsoft/pylance-release/discussions/2695
class AdbDevice(Device):
    pass


class AdbClient(Client):
    def devices_with_states(self) -> List[Tuple[Device, str]]:
        cmd = "host:devices"
        result: str = self._execute_cmd(cmd)

        devices = []
        for line in filter(None, result.split("\n")):
            try:
                serial, state = line.split()
            except ValueError:
                raise RuntimeError("Adb response parse error")

            device_with_state = (Device(self, serial), state)
            devices.append(device_with_state)

        return devices

    def devices(self, state=None) -> List[Device]:
        result = []
        for device, state_ in self.devices_with_states():
            if state is not None and state != state_:
                continue
            result.append(device)

        return result

    def device_with_state(self, serial: str):
        for device, status in self.devices_with_states():
            if device.serial == serial:
                return device, status

        return None, None


@contextmanager
def deviceRestricted(client: AdbClient, deviceName: str):
    try:
        device, state = client.device_with_state(deviceName)
    except (RuntimeError, ConnectionError):
        raise AdbConnectionError()

    if device is None:
        raise DeviceNotFound()

    assert state is not None
    if state != DEVICE_STATE_OK:
        if state == DEVICE_STATE_UNAUTHORIZED:
            raise DeviceStateUnauthorized()
        else:
            raise DeviceStateInvalid(state)

    try:
        yield device
    except (RuntimeError, ConnectionError) as e:
        raise DeviceRuntimeError(str(e))


def devicesRestricted(client: AdbClient):
    try:
        devices: List[AdbDevice] = client.devices()
    except (RuntimeError, ConnectionError):
        raise AdbConnectionError()

    if len(devices) == 0:
        raise NoDevicesFound()

    return devices
