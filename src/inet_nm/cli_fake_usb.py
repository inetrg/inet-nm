import argparse
import hashlib
import json
import os
import sys
from typing import Dict

from inet_nm._helpers import nm_print


def _save_fake_devices(devices: dict):
    path = os.getenv("INET_NM_FAKE_USB_PATH")
    if path is None:
        raise EnvironmentError(
            "To use fake USB devs one must set the INET_NM_FAKE_USB_PATH."
        )
    with open(path, "w") as f:
        json.dump(devices, f, sort_keys=True, indent=4)
    nm_print(f"Saved fake devices to {path}.")


def _get_fake_devices() -> Dict:
    path = os.getenv("INET_NM_FAKE_USB_PATH")
    if path is None:
        raise EnvironmentError(
            "To use fake USB devs one must set the INET_NM_FAKE_USB_PATH."
        )
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)


def add_board(id=None, **kwargs):
    # Read from env file for devices
    fake_devices = _get_fake_devices()
    if id is None:
        id = str(len(fake_devices))

    # Calculate a counter based off current boards
    board_counter = len(fake_devices)
    # Create an MD5 hash of the input string
    hash_object = hashlib.md5(id.encode())
    # Convert the hash to a hexadecimal string
    hex_hash = hash_object.hexdigest()

    ID_PATH = kwargs.get("ID_PATH", f"pci-0000:00:00.0-usb-0:{board_counter}")
    device_node = kwargs.get("device_node", f"/dev/ttyUSB{board_counter + 100}")
    ID_VENDOR_ID = kwargs.get("ID_VENDOR_ID", hex_hash[0:4])
    ID_MODEL_ID = kwargs.get("ID_MODEL_ID", hex_hash[5:8])
    ID_SERIAL_SHORT = kwargs.get("ID_SERIAL_SHORT", hex_hash[8:16])

    dev = [
        {
            "subsystem": "usb",
            "DEVTYPE": "usb_device",
            "parent": {
                "subsystem": "usb",
                "DEVTYPE": "usb_device",
            },
        },
        {
            "subsystem": "tty",
            "device_node": device_node,
            "parent": {
                "subsystem": "usb",
                "DEVTYPE": "usb_device",
                "ID_VENDOR_ID": ID_VENDOR_ID,
                "ID_MODEL_ID": ID_MODEL_ID,
                "ID_SERIAL_SHORT": ID_SERIAL_SHORT,
                "ID_MODEL_FROM_DATABASE": "USB Serial",
                "ID_VENDOR_FROM_DATABASE": "QinHeng Electronics",
                "DRIVER": "ch341",
                "ID_PATH": ID_PATH,
            },
        },
    ]
    fake_devices[id] = dev
    nm_print(f"Added fake device with ID {id}.")
    return fake_devices


def remove_board(id=None):
    fake_devices = _get_fake_devices()
    if len(fake_devices) == 0:
        nm_print("No fake devices to remove.")
        return
    if id is None:
        # If no ID, remove that last item in the dict after sorting
        id = sorted(fake_devices.keys())[-1]
    del fake_devices[id]
    nm_print(f"Removed fake device with ID {id}.")
    return fake_devices


def main():
    """Control the fake boards."""
    parser = argparse.ArgumentParser(
        description="Control fake usb devices, must have "
        "INET_NM_FAKE_USB_PATH env var set."
    )
    parser.add_argument(
        "--id",
        "-i",
        default=None,
        help="The ID of the fake id, if None a incrementing number will be assigned.",
    )
    parser.add_argument(
        "--remove",
        "-r",
        action="store_true",
        help="Remove a board with ID.",
    )
    parser.add_argument(
        "kwargs",
        nargs="*",
        help="Additional kwargs to add to the fake device, such as ID_VENDOR_ID=1234",
    )

    args = parser.parse_args()
    kwargs = {}
    for arg in args.kwargs:
        arg = arg.split("=")
        assert len(arg) == 2, f"Invalid arg {arg}"
        kwargs[arg[0]] = arg[1]

    if os.getenv("INET_NM_FAKE_USB_PATH") is None:
        nm_print("Please set the INET_NM_FAKE_USB_PATH env var... somewhere.")
        sys.exit(1)

    if args.remove:
        devs = remove_board(args.id)
    else:
        devs = add_board(args.id, **kwargs)

    _save_fake_devices(devs)


if __name__ == "__main__":
    main()
