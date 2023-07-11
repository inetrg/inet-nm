import argparse
import sys

import inet_nm.commissioner as cmr
import inet_nm.config as cfg


def main():
    """CLI to commission a USB board."""
    parser = argparse.ArgumentParser(description="Commission USB boards")
    cfg.config_arg(parser)
    parser.add_argument("-b", "--board", help="Name of the board to commission")
    parser.add_argument(
        "-n", "--no-cache", help="Ignore the cache", action="store_true"
    )
    parser.add_argument(
        "-m",
        "--mock-dev",
        help="Mock a device, useful for boards that do not have USB interfaces",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="Device will always be ignore, used for ttys that are connected "
        "but not part of the inet-nm ecosystem.",
        action="store_true",
    )

    args = parser.parse_args()
    nodes_cfg = cfg.NodesConfig(args.config)
    bi_cfg = cfg.BoardInfoConfig(args.config)
    # Check early since we will need to write eventually
    nodes_cfg.check_file(writable=True)
    bi_cfg.check_file(writable=False)

    saved_nodes = nodes_cfg.load()
    nm_nodes = (
        cmr.get_devices_from_tty()
        if args.no_cache
        else cmr.get_devices_from_tty(saved_nodes)
    )
    print(f"Found {len(saved_nodes)} saved nodes in {args.config}")
    if args.mock_dev:
        nm_nodes.append(cmr.mock_device())

    try:
        selected_node = cmr.select_available_node(nm_nodes)
    except ValueError:
        print("No available nodes found")
        sys.exit(1)
    except cmr.TtyNotPresent as exc:
        if args.mock_dev:
            selected_node = nm_nodes[-1]
        else:
            raise exc
    if args.ignore:
        selected_node.ignore = True
    else:
        binfo = bi_cfg.load()
        selected_node.board = args.board or cmr.select_board(
            list(binfo.keys()), selected_node
        )
        if selected_node.board in binfo:
            selected_node.features_provided = binfo[selected_node.board]

    nodes = cmr.add_node_to_nodes(saved_nodes, selected_node)
    nodes_cfg.save(nodes)
    print(f"Updated {nodes_cfg.file_path}")


if __name__ == "__main__":
    main()
