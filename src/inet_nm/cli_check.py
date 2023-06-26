import argparse
import json

import inet_nm.check as chk
import inet_nm.config as cfg


def main():
    """CLI entrypoint for counting the inventory of boards."""
    parser = argparse.ArgumentParser(description="Check the state of the boards")
    cfg.config_arg(parser)
    chk.check_args(parser)
    parser.add_argument(
        "--show-features", action="store_true", help="Shows all features for all boards"
    )
    args = parser.parse_args()
    kwargs = vars(args)
    show_features = kwargs.pop("show_features")

    nodes = chk.get_filtered_nodes(**kwargs)

    if show_features:
        info = chk.all_features_from_nodes(nodes)
    else:
        info = chk.nodes_to_boards(nodes)
    out = json.dumps(info, indent=2, sort_keys=True)
    print(out)


if __name__ == "__main__":
    main()
