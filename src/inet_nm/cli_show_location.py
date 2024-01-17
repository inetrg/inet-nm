import argparse
import json
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


def _main():
    """CLI to commission a USB board."""
    parser = argparse.ArgumentParser(description="Commission USB boards")
    cfg.config_arg(parser)
    chk.check_filter_args(parser)
    parser.add_argument(
        "-l",
        "--location-only",
        action="store_true",
        help="Show only the location names",
    )
    parser.add_argument(
        "-g",
        "--graph",
        help="If location names follow proper convention, then show a graph",
    )
    parser.add_argument(
        "-u",
        "--unassigned",
        action="store_true",
        help="Include nodes that have no matching location",
    )

    args = parser.parse_args()
    loc_cfg = cfg.LocationConfig(config_dir=args.config)
    loc_mapping = loc_cfg.load()

    kwargs = vars(args)
    location_only = kwargs.pop("location_only")
    graph = kwargs.pop("graph")
    unassigned = kwargs.pop("unassigned")
    nodes = chk.get_filtered_nodes(**kwargs)

    matching_locs = []
    for node in nodes:
        loc = get_location_from_node(node)
        if loc in loc_mapping or unassigned:
            if unassigned and loc not in loc_mapping:
                loc_name = "unassigned"
            else:
                loc_name = loc_mapping[loc]
            if location_only:
                matching_locs.append(loc_name)
            elif graph:
                pass
            else:
                data = {
                    "uid": node.uid,
                    "board": node.board,
                    "location": loc_name,
                }
                matching_locs.append(data)
    if len(matching_locs) and isinstance(matching_locs[0], list):
        matching_locs = sorted(matching_locs)
    print(json.dumps(matching_locs, indent=2, sort_keys=True))


def main():
    """CLI to commission a USB board."""
    try:
        _main()
    except KeyboardInterrupt:
        print("\nUser aborted...")


if __name__ == "__main__":
    main()
