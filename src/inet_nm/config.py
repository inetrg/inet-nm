"""Provide utilities for interacting with the inet_nm configuration.

It includes functionality for saving and loading information about
the boards and nodes, as well as for handling the path configuration.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Union

from inet_nm.data_types import NmNode


def _file_from_path(config_dir: Union[Path, str], file_name: str) -> Path:
    """
    Return a file path constructed from config_dir and file_name.

    Args:
        config_dir: Directory for the configuration files.
        file_name: Name of the file.

    Returns:
        The full path to the file.
    """
    config_dir = Path(config_dir).expanduser()
    file_path = config_dir / file_name
    config_dir.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def nodes_path(config_dir: Union[Path, str]) -> Path:
    """
    Get the path to the nodes file.

    Args:
        config_dir: Directory for the configuration files.

    Returns:
        The full path to the nodes file.
    """
    return _file_from_path(config_dir, "nodes.json")


def board_info_path(config_dir: Union[Path, str]) -> Path:
    """
    Get the path to the board info file.

    Args:
        config_dir: Directory for the configuration files.

    Returns:
        The full path to the board info file.
    """
    return _file_from_path(config_dir, "board_info.json")


def save_board_info(
    config_dir: Union[Path, str], board_info: Dict[str, Union[str, int]]
):
    """
    Write the board_info dict to a json file in the config_dir.

    Args:
        config_dir: Directory for the configuration files.
        board_info: Board information to save.
    """
    file_path = board_info_path(config_dir)
    with file_path.open("w") as file:
        json.dump(board_info, file, indent=2, sort_keys=True)


def load_board_info(config_dir: Union[Path, str]) -> List[str]:
    """
    Load and return the riot board info from a json file in the config_dir.

    Args:
        config_dir: Directory for the configuration files.

    Returns:
        The board information.
    """
    file_path = board_info_path(config_dir)
    if not file_path.exists():
        return []

    with file_path.open() as file:
        return json.load(file)


def load_nodes(config_dir: Union[Path, str]) -> List[NmNode]:
    """
    Load and return the nodes from a json file in the config_dir.

    Args:
        config_dir: Directory for the configuration files.

    Returns:
        The nodes.
    """
    file_path = nodes_path(config_dir)
    if not file_path.exists():
        return []

    with file_path.open() as file:
        data = json.load(file)

    return [NmNode.from_dict(item) for item in data]


def save_nodes(config_dir: Union[Path, str], boards: List[NmNode]):
    """
    Write the list of boards to a json file in the config_dir.

    Args:
        config_dir (Union[Path, str]): Directory for the configuration files.
        boards (List[NmNode]): List of boards to save.
    """
    file_path = nodes_path(config_dir)
    with file_path.open("w") as file:
        data = [board.to_dict() for board in boards]
        json.dump(data, file, indent=2)


def get_lock_path(config_dir: Union[Path, str]) -> Path:
    """
    Return the lock file path constructed from config_dir.

    Args:
        config_dir (Union[Path, str]): Directory for the configuration files.

    Returns:
        Path: The full path to the lock file.
    """
    config_dir = Path(config_dir).expanduser() / "locks"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def config_arg(parser: argparse.ArgumentParser):
    """
    Add a configuration argument to the provided parser.

    Args:
        parser (argparse.ArgumentParser): ArgumentParser object.
    """
    nm_config_dir = os.environ.get("NM_CONFIG_DIR", "~/.config/inet_nm")
    parser.add_argument(
        "-c",
        "--config",
        default=nm_config_dir,
        help="Path to the config dir, defaults to NM_CONFIG_DIR or "
        "~/.config/inet_nm if NM_CONFIG_DIR is not set",
    )
