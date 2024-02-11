import os
from typing import List, Optional

if os.getenv("INET_NM_FAKE_USB_PATH"):
    from inet_nm.fake_usb import Context
else:
    from pyudev import Context

from inet_nm.data_types import NmNode


class TtyNotPresent(Exception):
    """Exception to be raised when a TTY device is not found for a given NmNode."""


def get_connected_uids() -> List[str]:
    """
    Get the UIDs of all connected USB devices.

    Returns:
        A list of UIDs of all connected USB devices.
    """
    uids = []
    context = Context()
    for device in context.list_devices(subsystem="tty"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        vendor_id = parent.get("ID_VENDOR_ID")
        model_id = parent.get("ID_MODEL_ID")
        serial_short = parent.get("ID_SERIAL_SHORT")
        uids.append(NmNode.calculate_uid(model_id, vendor_id, serial_short))
    return uids


def get_connected_id_paths() -> List[str]:
    """
    Get the ID_PATHs of all connected USB devices.

    Returns:
        A list of ID_PATHs of all connected USB devices.
    """
    context = Context()
    locations = []
    for device in context.list_devices(subsystem="usb", DEVTYPE="usb_device"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        locations.append(device.get("ID_PATH"))
    return locations


def get_id_path_from_node(node: NmNode) -> str:
    """
    Get the ID_PATH of a connected USB device.

    Args:
        node: The node to get the ID_PATH for.

    Returns:
        The ID_PATH of the connected USB device.
    """
    context = Context()
    vendor_id = node.vendor_id
    model_id = node.product_id
    serial_short = node.serial

    for device in context.list_devices(subsystem="tty"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        if (
            parent.get("ID_VENDOR_ID") == vendor_id
            and parent.get("ID_MODEL_ID") == model_id
            and parent.get("ID_SERIAL_SHORT") == serial_short
        ):
            return device.get("ID_PATH")
    raise Exception("Node not found, maybe not connected")


def get_devices_from_tty(saved_nodes: Optional[List[NmNode]] = None) -> List[NmNode]:
    """
    Retrieve connected TTY devices as a list of NmNode objects.

    Args:
        saved_nodes: List of previously saved NmNode objects.

    Returns:
        List of NmNode objects representing connected TTY devices.

    Raises:
        TtyNotPresent: If a TTY device could not be found for a given NmNode.
    """
    saved_nodes = saved_nodes or []
    context = Context()
    nodes = []
    for device in context.list_devices(subsystem="tty"):
        if "ACM" in device.device_node or "USB" in device.device_node:
            usb_device = device.find_parent("usb", "usb_device")
            nm_node = NmNode(
                vendor_id=usb_device.get("ID_VENDOR_ID"),
                product_id=usb_device.get("ID_MODEL_ID"),
                serial=usb_device.get("ID_SERIAL_SHORT"),
                vendor=usb_device.get("ID_VENDOR_FROM_DATABASE"),
                model=usb_device.get("ID_MODEL_FROM_DATABASE"),
                driver=usb_device.get("DRIVER"),
            )

            if nm_node.uid in [node.uid for node in saved_nodes]:
                continue
            nodes.append(nm_node)
    return nodes


def get_ttys_from_nm_node(nm_node: NmNode) -> List[str]:
    """
    Retrieve the TTY device node string for a given NmNode.

    Args:
        nm_node: An NmNode object.

    Returns:
        The TTY device node string.

    Raises:
        TtyNotPresent: If a TTY device could not be found for the given NmNode.
    """
    context = Context()
    vendor_id = nm_node.vendor_id
    model_id = nm_node.product_id
    serial_short = nm_node.serial

    ttys = []

    for device in context.list_devices(subsystem="tty"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        if (
            parent.get("ID_VENDOR_ID") == vendor_id
            and parent.get("ID_MODEL_ID") == model_id
            and parent.get("ID_SERIAL_SHORT") == serial_short
        ):
            ttys.append(device.device_node)
    return ttys


def get_tty_from_nm_node(nm_node: NmNode) -> str:
    """
    Retrieve the TTY device node string for a given NmNode.

    Args:
        nm_node: An NmNode object.

    Returns:
        The TTY device node string.

    Raises:
        TtyNotPresent: If a TTY device could not be found for the given NmNode.
    """
    ttys = get_ttys_from_nm_node(nm_node)
    if ttys:
        return ttys[0]

    raise TtyNotPresent(f"Could not find tty device for {nm_node}")
