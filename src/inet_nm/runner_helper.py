import subprocess
import sys

import inet_nm.check as chk


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
