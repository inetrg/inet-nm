import argparse
import sys
from typing import List, Optional

import pyudev

import inet_nm.check as chk
import inet_nm.commissioner as cmr
import inet_nm.config as cfg
from inet_nm._helpers import (
    nm_prompt_choice,
    nm_prompt_confirm,
    nm_prompt_default_input,
)
from inet_nm.data_types import NmNode


def select_available_node(nodes: List[NmNode], mapped_locations: List[str]) -> NmNode:
    """
    Prompt the user to select an available node from a list of NmNode objects.

    Args:
        nodes: List of available NmNode objects.

    Returns:
        The selected NmNode.
    """
    nodes_to_select_from = []
    for node in nodes:
        loc = get_location_from_node(node)
        if loc not in mapped_locations:
            nodes_to_select_from.append(node)

    def _uid_board(node: NmNode):
        return f"{node.uid} {node.board}"

    return nm_prompt_choice("Select the node", nodes_to_select_from, _uid_board)


def get_locations_not_in_location(mapped_locations: List[str]):
    context = pyudev.Context()
    locations = []
    for device in context.list_devices(subsystem="usb", DEVTYPE="usb_device"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        loc = device.get("ID_PATH")
        print(loc)
        if loc not in mapped_locations:
            locations.append(loc)
    return locations


def get_location_from_node(node: NmNode) -> str:
    context = pyudev.Context()
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
    # TODO: raise some exception here
    return None


import re


def largest_matching_name(names):
    # Nested function to check if a string is a semantic version
    def is_matching_version(s):
        return bool(re.match(r"^\d+\.\d+\.\d+$", s))

    # Nested function to convert semantic version string "x.y.z" to tuple (x, y, z)
    def version_to_tuple(v):
        return tuple(map(int, v.split(".")))

    # Nested function to convert tuple (x, y, z) to semantic version string "x.y.z"
    def tuple_to_version(t):
        return ".".join(map(str, t))

    # Filter the list for semantic names, convert each to a tuple, and find the largest tuple
    matching_names = [v for v in names if is_matching_version(v)]
    largest_version_tuple = max(
        map(version_to_tuple, matching_names), default=(1, 1, 0)
    )

    return largest_version_tuple


def try_to_inc_map_name(names: List[str]) -> str:
    """Try to increment a name from a list of names.

    If default convention is followed: for example,
    1.1.1
    1.1.2
    1.1.3
    1.1.4 (every 4 nodes get bumped)
    1.2.1
    1.2.2
    1.2.3
    1.2.4
    2.1.1 (manual bump should continue from there)
    2.1.2
    2.1.3
    2.1.4
    2.2.1

    Args:
        names: List of names to check.

    Returns:
        The incremented name.
    """
    largest = largest_matching_name(names)
    if largest[2] < 4:
        largest = (largest[0], largest[1], largest[2] + 1)
    elif largest[1] < 4:
        largest = (largest[0], largest[1] + 1, 1)
    return f"{largest[0]}.{largest[1]}.{largest[2]}"


def _main():
    """CLI to commission a USB board."""
    parser = argparse.ArgumentParser(description="Commission USB boards")
    cfg.config_arg(parser)
    parser.add_argument("-u", "--uid", help="UID of the board to locate")
    parser.add_argument(
        "-l", "--locate", action="store_true", help="Use usb hub location"
    )

    args = parser.parse_args()
    loc_cfg = cfg.LocationConfig(config_dir=args.config)
    loc_mapping = loc_cfg.load()

    if args.locate:
        locations = get_locations_not_in_location(list(loc_mapping.keys()))
        location = nm_prompt_choice("Select location to name", locations)
    else:
        available = chk.get_filtered_nodes(config=args.config)
        # TODO: Remove the nodes that are currently mapped
        sel_node = select_available_node(available, list(loc_mapping.keys()))
        location = get_location_from_node(sel_node)
    def_name = try_to_inc_map_name(list(loc_mapping.values()))
    name = nm_prompt_default_input("Enter a name for the location", default=def_name)
    if location in loc_mapping:
        res = nm_prompt_confirm(
            f"Overwrite {location} currently " f"{loc_mapping[location]}?", default=True
        )
        if res:
            loc_mapping[location] = name
    else:
        loc_mapping[location] = name
    loc_cfg.save(loc_mapping)
    print(f"{name} mapped to {location}")
    print(f"Updated {loc_cfg.file_path}")


def main():
    """CLI to commission a USB board."""
    try:
        _main()
    except KeyboardInterrupt:
        print("\nUser aborted...")


if __name__ == "__main__":
    main()
