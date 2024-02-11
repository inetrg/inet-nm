import argparse
from typing import List

import inet_nm.check as chk
import inet_nm.config as cfg
from inet_nm._helpers import (
    nm_print,
    nm_prompt_choice,
    nm_prompt_confirm,
    nm_prompt_default_input,
    try_to_inc_map_name,
)
from inet_nm.data_types import NmNode
from inet_nm.usb_ctrl import get_connected_id_paths, get_id_path_from_node


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
        loc = get_id_path_from_node(node)
        if loc not in mapped_locations:
            nodes_to_select_from.append(node)

    def _uid_board(node: NmNode):
        return f"{node.uid} {node.board}"

    return nm_prompt_choice("Select the node", nodes_to_select_from, _uid_board)


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
        con_locs = get_connected_id_paths()
        mapped_locs = list(loc_mapping.keys())
        locations = [loc for loc in con_locs if loc not in mapped_locs]
        location = nm_prompt_choice("Select location to name", locations)
    else:
        available = chk.get_filtered_nodes(config=args.config)
        sel_node = select_available_node(available, list(loc_mapping.keys()))
        location = get_id_path_from_node(sel_node)
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
    nm_print(f"{name} mapped to {location}")
    nm_print(f"Updated {loc_cfg.file_path}")


def main():
    """CLI to commission a USB board."""
    try:
        _main()
    except KeyboardInterrupt:
        nm_print("\nUser aborted...")


if __name__ == "__main__":
    main()
