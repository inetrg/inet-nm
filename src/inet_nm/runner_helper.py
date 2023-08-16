import subprocess
import sys

import inet_nm.check as chk
import inet_nm.config as cfg


def _is_command_available(cmd):
    return_code = subprocess.call(
        f"which {cmd}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    if return_code != 0:
        print(f"{cmd} is not available! Please install first.")
        sys.exit(1)


def _check_filtered_nodes(**kwargs):
    nodes = chk.get_filtered_nodes(**kwargs)
    if len(nodes) == 0:
        print("No available nodes!")
        sys.exit(1)
    return nodes


def node_env_vars(config: str):
    env_cfg = cfg.EnvConfig(config)
    env_cfg.check_file(writable=False)
    env_info = env_cfg.load()
    pattern_nodes = {}
    for pattern in env_info.patterns:
        pattern["config"] = config
        env_key = pattern.pop("key")
        env_val = pattern.pop("val")
        matched_nodes = chk.get_filtered_nodes(all_nodes=True, **pattern)
        for node in matched_nodes:
            if node.uid not in pattern_nodes:
                pattern_nodes[node.uid] = {}
            pattern_nodes[node.uid][env_key] = env_val
    for uid, env in env_info.nodes.items():
        for key, val in env.items():
            if uid not in pattern_nodes:
                pattern_nodes[uid] = {}
            pattern_nodes[uid][key] = val
    env_info.nodes = pattern_nodes
    return env_info


def sanity_check(cmd, **kwargs):
    """Checks if the command is available and if there are any nodes available.

    Args:
        cmd (str): Command to check.
        **kwargs: Keyword arguments to pass to check.get_filtered_nodes.

    Returns:
        List of NmNode objects.
    """
    _is_command_available(cmd)
    return _check_filtered_nodes(**kwargs)


def do_nothing(signum, frame):
    """Does nothing."""
    pass
