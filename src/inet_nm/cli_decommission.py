import argparse
import sys

import inet_nm.check as chk
import inet_nm.commissioner as cmr
import inet_nm.config as cfg


def main():
    """CLI to commission a USB board."""
    parser = argparse.ArgumentParser(description="Decommission USB boards")
    cfg.config_arg(parser)
    parser.add_argument(
        "-a", "--all", help="Remove all selected nodes", action="store_true"
    )
    parser.add_argument(
        "-m", "--missing", help="Select missing nodes", action="store_true"
    )

    args = parser.parse_args()
    nodes_cfg = cfg.NodesConfig(args.config)
    nodes_cfg.check_file(writable=True)

    saved_nodes = nodes_cfg.load()

    if args.missing:
        nodes_to_remove = chk.check_nodes(saved_nodes, missing=True)
    else:
        nodes_to_remove = chk.check_nodes(saved_nodes, all_nodes=True, used=True)

    nodes = saved_nodes
    if args.all:
        for node in nodes_to_remove:
            nodes = cmr.remove_node_to_nodes(nodes, node)
    else:
        try:
            selected_node = cmr.select_available_node(nodes_to_remove)
            nodes = cmr.remove_node_to_nodes(nodes, selected_node)
            print("Removed node:")
            print(f"    UID: {selected_node.uid}")
            print(f"    PID: {selected_node.product_id}")
            print(f"    VID: {selected_node.vendor_id}")
            print(f"    SN:  {selected_node.serial}")
        except ValueError:
            print("No available nodes found")
            sys.exit(1)

    nodes_cfg.save(nodes)

    print(f"Updated {nodes_cfg.file_path}")


if __name__ == "__main__":
    main()
