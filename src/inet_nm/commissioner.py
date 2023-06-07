"""This module commissions USB boards."""
import argparse
import sys
from typing import List, Optional

import pyudev

import inet_nm.config as cfg
from inet_nm._helpers import nm_prompt_choice, nm_prompt_confirm, nm_prompt_input
from inet_nm.data_types import NmNode


class TtyNotPresent(Exception):
    """Exception to be raised when a TTY device is not found for a given NmNode."""


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
    context = pyudev.Context()
    vendor_id = nm_node.vendor_id
    model_id = nm_node.product_id
    serial_short = nm_node.serial

    for device in context.list_devices(subsystem="tty"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        if (
            parent.get("ID_VENDOR_ID") == vendor_id
            and parent.get("ID_MODEL_ID") == model_id
            and parent.get("ID_SERIAL_SHORT") == serial_short
        ):
            return device.device_node

    raise TtyNotPresent(f"Could not find tty device for {nm_node}")


def select_available_node(nodes: List[NmNode]) -> NmNode:
    """
    Prompt the user to select an available node from a list of NmNode objects.

    Args:
        nodes: List of available NmNode objects.

    Returns:
        The selected NmNode.
    """

    def _nice_node(node: NmNode):
        msg = f"{get_tty_from_nm_node(node)} {node.vendor}"
        if node.model:
            msg += f" {node.model}"
        msg += f" {node.serial}"
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


def commission():
    """CLI to commission a USB board."""
    parser = argparse.ArgumentParser(description="Commission USB boards")
    cfg.config_arg(parser)
    parser.add_argument("-b", "--board", help="Name of the board to commission")
    parser.add_argument(
        "-n", "--no-cache", help="Ignore the cache", action="store_true"
    )

    args = parser.parse_args()
    nodes_cfg = cfg.NodesConfig(args.config)
    bi_cfg = cfg.BoardInfoConfig(args.config)
    # Check early since we will need to write eventually
    nodes_cfg.check_file(writable=True)
    bi_cfg.check_file(writable=False)

    saved_nodes = nodes_cfg.load()
    nm_nodes = (
        get_devices_from_tty() if args.no_cache else get_devices_from_tty(saved_nodes)
    )
    print(f"Found {len(saved_nodes)} saved nodes in {args.config}")

    try:
        selected_node = select_available_node(nm_nodes)
    except ValueError:
        print("No available nodes found")
        return
    binfo = bi_cfg.load()
    selected_node.board = select_board(list(binfo.keys()), selected_node)
    if selected_node.board in binfo:
        selected_node.features_provided = binfo[selected_node.board]

    nodes = add_node_to_nodes(saved_nodes, selected_node)
    nodes_cfg.save(nodes)
    print(f"Updated {nodes_cfg.file_path}")


def update_commissioned():
    """Go through the list of commissioned nodes and update features."""
    parser = argparse.ArgumentParser(description="Update commissioned features")
    cfg.config_arg(parser)
    args = parser.parse_args()

    nodes_cfg = cfg.NodesConfig(args.config)
    bi_cfg = cfg.BoardInfoConfig(args.config)

    nodes_cfg.check_file(writable=True)
    bi_cfg.check_file(writable=False)

    binfo = bi_cfg.load()
    nodes = nodes_cfg.load()
    for node in nodes:
        if node.board in binfo:
            node.features_provided = binfo[node.board]
    nodes_cfg.save(nodes)
    print(f"Updated {nodes_cfg.file_path}")


def cli_tty_from_uid():
    """CLI to get the TTY device node string for a given NmNode UID."""
    parser = argparse.ArgumentParser(
        description="Get the TTY device node string for a given NmNode UID."
    )
    cfg.config_arg(parser)
    parser.add_argument("uid", help="Node UID string.")
    args = parser.parse_args()

    nodes_cfg = cfg.NodesConfig(args.config)
    nodes_cfg.check_file(writable=False)

    nodes = nodes_cfg.load()
    try:
        node = next(node for node in nodes if node.uid == args.uid)
    except StopIteration:
        print(f"Could not find node with UID {args.uid}")
        return
    try:
        print(get_tty_from_nm_node(node))
    except TtyNotPresent:
        print(f"Could not find TTY device for {node.board} with SN {node.serial}")
        sys.exit(1)
    sys.exit(0)
