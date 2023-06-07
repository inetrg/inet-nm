import argparse
import os
import subprocess
from pathlib import Path
from typing import List

import inet_nm.config as cfg


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
        print(f"Getting features_provided for {bn}")
        env = os.environ.copy()
        env[board_env_var] = bn
        res = subprocess.run(cmd.split(), cwd=cwd, env=env, capture_output=True)
        if res.returncode != 0:
            errors.append(bn)
            print(f"FAILED to run {cmd} for {bn}")
        boards[bn] = res.stdout.decode().split()
    if errors:
        raise RuntimeError(f"Failed to run {cmd} for {errors}")
    return boards


def cli_update_boards_from_os():
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
        bns = _get_names(args.board_info, args.basedir)
        board_info = _get_features_provided(
            args.board_features, args.basedir, args.board_env_var, bns
        )
        cfg.save_board_info(args.config, board_info)
        print(f"\nUpdated {cfg.board_info_path(args.config)}")
    except KeyboardInterrupt:
        print("\nUser aborted")
    except RuntimeError as e:
        print(f"\nError: {e}")
