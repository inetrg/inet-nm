import argparse

import inet_nm.config as cfg


def main():
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


if __name__ == "__main__":
    main()
