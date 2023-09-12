import argparse
import signal
import sys

import inet_nm.check as chk
import inet_nm.config as cfg
import inet_nm.runner_apps as apps
import inet_nm.runner_helper as rh


def main():
    """CLI entrypoint for executing a command on each node."""
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
        "-F", "--force", action="store_true", help="Force execution of command."
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=None,
        help="Wait until node available in seconds.",
    )
    parser.add_argument(
        "--seq",
        action="store_true",
        help="Run commands sequentially instead of concurrently",
    )
    parser.add_argument(
        "-r",
        "--output-filter",
        type=str,
        default=None,
        help="Filter all lines with regex.",
    )
    parser.add_argument(
        "-j",
        "--json-filter",
        action="store_true",
        help="Capture only json output.",
    )

    cfg.config_arg(parser)
    chk.check_args(parser)
    args = parser.parse_args()
    kwargs = vars(args)
    timeout = kwargs.pop("timeout")
    cmd = kwargs.pop("cmd")
    seq = kwargs.pop("seq")
    force = kwargs.pop("force")
    output_filter = kwargs.pop("output_filter")
    json_filter = kwargs.pop("json_filter")
    nodes = rh.sanity_check("/bin/bash", **kwargs)

    extra_env = rh.node_env_vars(args.config)
    # Somehow allows cleanup to happen...
    signal.signal(signal.SIGHUP, rh.do_nothing)
    try:
        with apps.NmShellRunner(
            nodes, default_timeout=timeout, seq=seq, extra_env=extra_env, force=force
        ) as runner:
            runner.cmd = cmd
            runner.output_filter = output_filter
            runner.json_filter = json_filter
            runner.run()
    except KeyboardInterrupt:
        print()
        print("User aborted!")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
