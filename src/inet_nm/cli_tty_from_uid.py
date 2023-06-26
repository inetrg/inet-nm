import argparse
import sys

import inet_nm.commissioner as cmr
import inet_nm.config as cfg


def main():
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
        print(cmr.get_tty_from_nm_node(node))
    except cmr.TtyNotPresent:
        print(f"Could not find TTY device for {node.board} with SN {node.serial}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
