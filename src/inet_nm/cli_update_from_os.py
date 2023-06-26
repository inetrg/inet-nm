import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List

import inet_nm.config as cfg
from inet_nm._helpers import nm_print, nm_prompt_confirm


def _get_names(cmd: str, cwd: Path) -> List[str]:
    """Call make info-boards and parse the output to a list."""
    res = subprocess.run(cmd.split(), cwd=cwd, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to run {cmd}")
    return res.stdout.decode().split()


def _get_features_provided(
    cmd: str, cwd: Path, board_env_var: str, board_names: List[str]
):
    boards = {}
    errors = []
    for bn in board_names:
        nm_print(f"Getting features_provided for {bn}")
        env = os.environ.copy()
        env[board_env_var] = bn
        # It seems resolving env vars isn't so easy
        # As a test requires echo of a board var, let's just resolve it...
        board_cmd = cmd.replace(f"${{{board_env_var}}}", bn)
        res = subprocess.run(board_cmd.split(), cwd=cwd, env=env, capture_output=True)

        if res.returncode != 0:
            errors.append(bn)
            nm_print(f"FAILED to run {cmd} for {bn}")
        boards[bn] = res.stdout.decode().split()
    return (boards, errors)


def main():
    """CLI entrypoint for updating the board info from the OS."""
    parser = argparse.ArgumentParser(description="Cache a list of boards")
    cfg.config_arg(parser)
    parser.add_argument("basedir", type=Path, help="Path to the board path directory")
    parser.add_argument(
        "-i",
        "--board-info",
        type=str,
        default="make info-boards",
        help="Command to get board info, defaults to 'make info-boards'",
    )
    parser.add_argument(
        "-f",
        "--board-features",
        type=str,
        default="make info-features-provided",
        help="Command to get board features, defaults to 'make info-features-provided'",
    )
    parser.add_argument(
        "-n",
        "--board-env-var",
        type=str,
        default="BOARD",
        help="The env var to indicate the board name for features provided,"
        "defaults to 'BOARD'",
    )

    args = parser.parse_args()

    try:
        bi_cfg = cfg.BoardInfoConfig(args.config)

        bi_cfg.check_file(writable=True)

        bns = _get_names(args.board_info, args.basedir)
        board_info, errors = _get_features_provided(
            args.board_features, args.basedir, args.board_env_var, bns
        )
        if errors:
            nm_print(f"Failed to get {args.board_features} for {errors}")
            if not nm_prompt_confirm("Write boards anyways", default=False):
                sys.exit(1)
        bi_cfg.save(board_info)
        nm_print(f"\nUpdated {bi_cfg.file_path}")
    except KeyboardInterrupt:
        nm_print("\nUser aborted")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
