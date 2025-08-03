from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ppadb.client import Client
from ppadb.device import Device

from galog.app.settings.settings import readSettings, writeSettings

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

_NOT_AVAIL = "<N/A>"
_PROP_MANUFACTURER = "ro.product.manufacturer"
_PROP_MODEL = "ro.product.model"
_PROP_RELEASE = "ro.build.version.release"
_PROP_CPU_ARCH = "ro.product.cpu.abi"
_PROP_SDK_MIN = "ro.build.version.min_supported_target_sdk"
_PROP_SDK_MAX = "ro.build.version.sdk"
_PROP_CODENAME1 = "ro.product.device"
_PROP_CODENAME2 = "ro.product.name"


@dataclass
class DeviceDetails:
    displayName: str
    osInfo: str
    cpuArch: str
    sdkVerMin: str
    sdkVerMax: str


@dataclass
class DeviceInfo:
    serial: str
    state: str
    details: Optional[DeviceDetails] = None


class AdbDevice(Device):
    def _device_display_name(self, props: Dict[str, str]):
        try:
            mf = props[_PROP_MANUFACTURER].capitalize()
            codename = props[_PROP_CODENAME1] or props[_PROP_CODENAME2]
            model = props[_PROP_MODEL]
        except KeyError:
            return _NOT_AVAIL

        if model.lower().startswith(mf.lower()):
            return f"{model} ({codename})"
        else:
            return f"{mf} {model} ({codename})"

    def _device_os_info(self, props: Dict[str, str]):
        try:
            osVer = props[_PROP_RELEASE]
        except KeyError:
            return _NOT_AVAIL

        return f"Android {osVer}"

    def details(self):
        props = self.get_properties()
        return DeviceDetails(
            displayName=self._device_display_name(props),
            cpuArch=props.get(_PROP_CPU_ARCH, _NOT_AVAIL),
            sdkVerMin=props.get(_PROP_SDK_MIN, _NOT_AVAIL),
            sdkVerMax=props.get(_PROP_SDK_MAX, _NOT_AVAIL),
            osInfo=self._device_os_info(props),
        )


class AdbClient(Client):
    def create_connection(self, timeout: Optional[float] = None):
        return super().create_connection(timeout=timeout or 5.0)

    def devices_with_states(self) -> List[Tuple[AdbDevice, str]]:
        cmd = "host:devices"
        result: str = self._execute_cmd(cmd)

        devices = []
        for line in filter(None, result.split("\n")):
            try:
                serial, state = line.split()
            except ValueError:
                raise RuntimeError("Adb response parse error")

            devices.append((AdbDevice(self, serial), state))

        return devices

    def devices(self, state=None) -> List[AdbDevice]:
        result = []
        for device, state_ in self.devices_with_states():
            if state is not None and state != state_:
                continue
            result.append(device)

        return result

    def device_with_state(self, serial: str):
        for device, state in self.devices_with_states():
            if device.serial == serial:
                return device, state

        return None, None


@contextmanager
def deviceRestricted(deviceSerial: str, client: AdbClient):
    try:
        device, state = client.device_with_state(deviceSerial)
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


def deviceList(client: AdbClient):
    try:
        devices = client.devices()
    except (RuntimeError, ConnectionError):
        raise AdbConnectionError()

    if len(devices) == 0:
        raise NoDevicesFound()

    return devices


def deviceListWithInfo(client: AdbClient) -> List[DeviceInfo]:
    try:
        devices = client.devices_with_states()
    except (RuntimeError, ConnectionError):
        raise AdbConnectionError()

    if len(devices) == 0:
        raise NoDevicesFound()

    result = []
    for device, state in devices:
        if state == DEVICE_STATE_OK:
            result.append(DeviceInfo(device.serial, state, device.details()))
        else:
            result.append(DeviceInfo(device.serial, state))

    return result


def adbClient():
    settings = readSettings()
    ipAddr = str(settings.adb.ipAddr)
    port = int(settings.adb.port)
    return AdbClient(ipAddr, port)