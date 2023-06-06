import argparse

import inet_nm.check as check
import inet_nm.config as cfg
import inet_nm.runner_apps as apps


def nm_tmux():
    parser = argparse.ArgumentParser(description="Commission USB boards")
    parser.add_argument(
        "-w", "--window", action="store_true", help="Open a window for each node."
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
    nodes = check.get_filtered_nodes(**kwargs)
    if len(nodes) == 0:
        print("No available nodes!")
        return
    if window:
        with apps.NmTmuxWindowedRunner(nodes, default_timeout=timeout) as runner:
            runner.cmd = cmd
            runner.run()
    else:
        with apps.NmTmuxPanedRunner(nodes, default_timeout=timeout) as runner:
            runner.cmd = cmd
            runner.run()


def nm_exec():
    parser = argparse.ArgumentParser(description="Commission USB boards")
    parser.add_argument(
        "cmd", type=str, help="Command to send after starting tmux session."
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
    nodes = check.get_filtered_nodes(**kwargs)
    if len(nodes) == 0:
        print("No available nodes!")
        return
    with apps.NmShellRunner(nodes, default_timeout=timeout) as runner:
        runner.cmd = cmd
        runner.run()
