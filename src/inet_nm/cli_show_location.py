import argparse
import json

import inet_nm.check as chk
import inet_nm.config as cfg
from inet_nm._helpers import nm_print
from inet_nm.graph import parse_locations
from inet_nm.usb_ctrl import get_id_path_from_node


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
        action="store_true",
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
        loc = get_id_path_from_node(node)
        if loc in loc_mapping or unassigned:
            if unassigned and loc not in loc_mapping:
                loc_name = "unassigned"
            else:
                loc_name = loc_mapping[loc]
            if location_only or graph:
                matching_locs.append(loc_name)
            else:
                data = {
                    "uid": node.uid,
                    "board": node.board,
                    "location": loc_name,
                }
                matching_locs.append(data)
    if len(matching_locs) and isinstance(matching_locs[0], list):
        matching_locs = sorted(matching_locs)
    if graph:
        names = [usb_info["name"] for usb_info in matching_locs]
        nm_print(parse_locations(names))
    else:
        nm_print(json.dumps(matching_locs, indent=2, sort_keys=True))


def main():
    """CLI to commission a USB board."""
    try:
        _main()
    except KeyboardInterrupt:
        nm_print("\nUser aborted...")


if __name__ == "__main__":
    main()
