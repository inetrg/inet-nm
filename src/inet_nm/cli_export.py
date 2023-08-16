import argparse

import inet_nm.check as chk
import inet_nm.config as cfg


def main():
    """CLI entrypoint for entering env vars."""
    parser = argparse.ArgumentParser(
        description="Export env vars, if specific nodes are selected one may "
        "need to reapply"
    )
    cfg.config_arg(parser)
    chk.check_args(parser)
    parser.add_argument(
        "--apply-pattern",
        action="store_true",
        help="Env var will be applied to the following pattern rather than a "
        "specific node",
    )
    parser.add_argument(
        "--apply-to-shared",
        action="store_true",
        help="Env var will be applied to every node regardless of matching",
    )
    parser.add_argument("key", type=str, help="The env var key")
    parser.add_argument("val", type=str, help="The env var value")
    args = parser.parse_args()
    kwargs = vars(args)

    apply_pattern = kwargs.pop("apply_pattern")
    apply_to_shared = kwargs.pop("apply_to_shared")
    env_key = str(kwargs.pop("key"))
    env_val = str(kwargs.pop("val"))

    env_cfg = cfg.EnvConfig(args.config)
    env_cfg.check_file(writable=True)

    env_info = env_cfg.load()
    if apply_to_shared:
        env_info.shared[env_key] = env_val
        print(f"Added {env_key}={env_val} to shared env vars")
    else:
        if apply_pattern:
            pattern = {}
            pattern["key"] = env_key
            pattern["val"] = env_val
            pattern["boards"] = args.boards
            pattern["feat_filter"] = args.feat_filter
            pattern["feat_eval"] = args.feat_eval
            # NOTE: All useful patterns must be added here
            env_info.patterns.append(pattern)
            print(f"Added patterns: {pattern}")
        else:
            nodes = chk.get_filtered_nodes(**kwargs)
            uids = {node.uid for node in nodes}
            for uid in uids:
                if uid not in env_info.nodes:
                    env_info.nodes[uid] = {}
                env_info.nodes[uid][env_key] = env_val
            print(f"Added {env_key}={env_val} to env vars for nodes {uids}")

    env_cfg.save(env_info)
    print(f"Written to {env_cfg.file_path}")


if __name__ == "__main__":
    main()
