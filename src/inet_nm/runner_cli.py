import argparse
import subprocess
import sys

import inet_nm.check as check
import inet_nm.config as cfg
import inet_nm.runner_apps as apps


def _is_command_available(cmd):
    return_code = subprocess.call(
        f"which {cmd}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    if return_code != 0:
        print(f"{cmd} is not available! Please install first.")
        sys.exit(1)


def _check_filtered_nodes(**kwargs):
    nodes = check.get_filtered_nodes(**kwargs)
    if len(nodes) == 0:
        print("No available nodes!")
        sys.exit(1)
    return nodes


def _sanity_check(cmd, **kwargs):
    _is_command_available(cmd)
    return _check_filtered_nodes(**kwargs)


def nm_tmux():
    parser = argparse.ArgumentParser(
        description="Starts interactive sessions for each node."
    )
    parser.add_argument(
        "-w", "--window", action="store_true", help="Open a window for each node."
    )
    parser.add_argument(
        "-n", "--session-name", default="default", help="Name of the tmux session."
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=None,
        help="Wait until node available in seconds.",
    )
    parser.add_argument(
        "-x",
        "--cmd",
        type=str,
        default=None,
        help="Command to send after starting tmux session.",
    )
    cfg.config_arg(parser)
    check.check_args(parser)
    args = parser.parse_args()
    kwargs = vars(args)
    window = kwargs.pop("window")
    timeout = kwargs.pop("timeout")
    cmd = kwargs.pop("cmd")
    sname = kwargs.pop("session_name")
    nodes = _sanity_check("tmux", **kwargs)
    if window:
        with apps.NmTmuxWindowedRunner(nodes, default_timeout=timeout) as runner:
            runner.cmd = cmd
            runner.session_name = sname
            runner.run()
    else:
        with apps.NmTmuxPanedRunner(nodes, default_timeout=timeout) as runner:
            runner.cmd = cmd
            runner.session_name = sname
            runner.run()


def nm_exec():
    parser = argparse.ArgumentParser(
        description="Execute command for each note environment."
    )
    parser.add_argument(
        "cmd",
        type=str,
        help="bash command to execute, ' must be escaped and generally pay"
        " attention to escape characters.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=None,
        help="Wait until node available in seconds.",
    )

    cfg.config_arg(parser)
    check.check_args(parser)
    args = parser.parse_args()
    kwargs = vars(args)
    timeout = kwargs.pop("timeout")
    cmd = kwargs.pop("cmd")
    nodes = nodes = _sanity_check("/bin/bash", **kwargs)
    with apps.NmShellRunner(nodes, default_timeout=timeout) as runner:
        runner.cmd = cmd
        runner.run()
