"""This module commissions USB boards."""
import random
import time
from typing import List

try:
    from cp210x import cp210x
except ImportError:
    cp210x = None

import inet_nm._helpers as hlp
from inet_nm._helpers import nm_prompt_choice, nm_prompt_confirm, nm_prompt_input
from inet_nm.data_types import NmNode
from inet_nm.usb_ctrl import get_ttys_from_nm_node


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
