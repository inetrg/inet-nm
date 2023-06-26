import argparse
import signal
import subprocess
import sys

import inet_nm.check as chk
import inet_nm.config as cfg
import inet_nm.runner_apps as apps
import inet_nm.runner_helper as rh


def _kill_tmux(session_name):
    output = subprocess.check_output(["tmux", "list-sessions"]).decode("utf-8")
    sessions = [line.split(":")[0] for line in output.split("\n") if line]
    for session in sessions:
        if session != session_name:
            continue
        print(f"Closing session {session}")
        subprocess.run(["tmux", "kill-session", "-t", session])
    exit(1)


def main():
    """CLI entrypoint for starting tmux sessions."""
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
    chk.check_args(parser)
    args = parser.parse_args()
    kwargs = vars(args)
    window = kwargs.pop("window")
    timeout = kwargs.pop("timeout")
    cmd = kwargs.pop("cmd")
    sname = kwargs.pop("session_name")
    nodes = rh.sanity_check("tmux", **kwargs)
    signal.signal(signal.SIGINT, lambda x, y: _kill_tmux(sname))

    # This is a hack to keep the process alive long enough
    # to remove the lockfiles
    # It seems the tmux session will still remain but at least
    # the lockfiles will be removed...
    signal.signal(signal.SIGHUP, rh.do_nothing)
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
    sys.exit(0)


if __name__ == "__main__":
    main()
