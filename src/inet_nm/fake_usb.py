import json
import os


class Device:
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def find_parent(self, subsystem=None, DEVTYPE=None, **kwargs):
        kwargs["subsystem"] = subsystem
        kwargs["DEVTYPE"] = DEVTYPE
        if "parent" in self.kwargs:
            return Device(self.kwargs["parent"])
        return None

    def get(self, key):
        return self.kwargs[key]

    @property
    def device_node(self):
        return self.kwargs.get("device_node", "")


class Context:
    def list_devices(self, subsystem=None, DEVTYPE=None, **kwargs):
        kwargs["subsystem"] = subsystem
        kwargs["DEVTYPE"] = DEVTYPE
        # Load from USB dev path .json
        path = os.getenv("INET_NM_FAKE_USB_PATH")
        if path is None:
            raise EnvironmentError(
                "To use fake USB devs one must set the INET_NM_FAKE_USB_PATH."
            )
        with open(path, "r") as f:
            fake_devices = json.load(f)
        ldevs = []
        for devs in fake_devices.values():
            ldevs.extend(devs)
        for device in ldevs:
            if all([device.get(key, None) == kwargs[key] for key in kwargs]):
                yield Device(device)
