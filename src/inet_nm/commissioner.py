"""This module commissions USB boards."""
import random
import time
from typing import List, Optional

import pyudev

try:
    from cp210x import cp210x
except ImportError:
    cp210x = None

import inet_nm._helpers as hlp
from inet_nm._helpers import nm_prompt_choice, nm_prompt_confirm, nm_prompt_input
from inet_nm.data_types import NmNode


class TtyNotPresent(Exception):
    """Exception to be raised when a TTY device is not found for a given NmNode."""


def check_and_set_uninitialized_sn(node: NmNode, sns: List = None):
    """
    Check if a given NmNode has an uninitialized serial number and prompt the user
    to set it.

    Args:
        node: An NmNode object.
        sns: List of serial numbers to check against.
    """

    if cp210x is None:
        return
    sns = sns or ["0001"]
    if node.serial not in sns:
        return

    pid_vid_sn = {
        "idVendor": int(node.vendor_id, 16),
        "idProduct": int(node.product_id, 16),
    }
    for usbdev in cp210x.Cp210xProgrammer.list_devices([pid_vid_sn]):
        # We only take the first one that matches
        if usbdev.serial_number != node.serial:
            continue

        dev = cp210x.Cp210xProgrammer(usbdev)

        random.seed()
        sn = f"INET-NM-{random.randint(0, 10**20)}".zfill(20)
        hlp.nm_print(f"Found uninitialized serial number ({node.serial})")
        sn = hlp.nm_prompt_default_input("Enter serial number", sn)

        dev.set_values({"serial_number": sn})
        # It seems there is some issues with reset.
        # Without a reset the device SN does not change properly.
        # With the reset some exceptions get thrown but the SN is set.
        # This is a quick fix.
        time.sleep(1)
        try:

            def _junk(x):
                pass

            cp210x.Cp210xProgrammer.__del__ = _junk
            dev.reset()
        except Exception:
            pass

        node.serial = sn
        node.uid = node.calculate_uid(node.product_id, node.vendor_id, node.serial)
        hlp.nm_print(f"Wrote {sn} to serial number in EEPROM.")
        return


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
    context = pyudev.Context()
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
    context = pyudev.Context()
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


def select_available_node(nodes: List[NmNode]) -> NmNode:
    """
    Prompt the user to select an available node from a list of NmNode objects.

    Args:
        nodes: List of available NmNode objects.

    Returns:
        The selected NmNode.
    """

    uids = list()

    def _nice_node(node: NmNode):
        nonlocal uids
        ttys = get_ttys_from_nm_node(node)
        if ttys:
            tty = ttys[uids.count(node.uid)]
        else:
            tty = "Unknown"
        msg = f"{tty} {node.vendor}"
        if node.model:
            msg += f" {node.model}"
        msg += f" {node.serial}"
        uids.append(node.uid)
        return msg

    return nm_prompt_choice("Select the node", nodes, _nice_node)


def add_node_to_nodes(nodes: List[NmNode], node: NmNode) -> List[NmNode]:
    """
    Add a new NmNode to a list of existing NmNode objects.

    Replaces any existing NmNode with the same UID.

    Args:
        nodes: List of existing NmNode objects.
        node: New NmNode to be added.

    Returns:
        Updated list of NmNode objects.
    """
    nodes = (
        [node if n.uid == node.uid else n for n in nodes]
        if any(n.uid == node.uid for n in nodes)
        else nodes + [node]
    )
    return nodes


def remove_node_to_nodes(nodes: List[NmNode], node: NmNode) -> List[NmNode]:
    """
    Remove an NmNode from a list of existing NmNode objects.

    Args:
        nodes: List of existing NmNode objects.
        node: NmNode to be removed.

    Returns:
        Updated list of NmNode objects.
    """
    nodes = [n for n in nodes if n.uid != node.uid]
    return nodes


def select_board(board_names: List[str], node: NmNode) -> str:
    """
    Prompts the user to select a board for a given NmNode.

    Args:
        board_names: List of available board names.
        node: NmNode for which to select a board.

    Returns:
        The selected board name.
    """
    msg = f"Select board name for {node.vendor}"
    if node.model:
        msg += f" {node.model}"
    while True:
        board = nm_prompt_input(msg, board_names)
        if board in board_names:
            return board
        if nm_prompt_confirm(
            f"Board {board} not in board list, continue?", default=False
        ):
            return board


def mock_device():
    """Mock a device, useful for boards that do not have USB interfaces"""

    sn = f"{random.randint(0, 10**20)}".zfill(20)
    sn = hlp.nm_prompt_default_input("Enter serial number", sn)
    return NmNode(
        vendor_id="1234",
        product_id="5678",
        serial=sn,
        vendor="generic_vendor",
        driver="mock",
        mock=True,
    )
