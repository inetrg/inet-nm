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


class _ConfigFile:
    _FILENAME = None
    _LOAD_TYPE = None

    def __init__(self, config_dir: Union[Path, str]):
        config_dir = Path(config_dir)
        self.file_path = Path(config_dir / self._FILENAME).expanduser()

    def check_file(self, writable: bool = False) -> bool:
        """
        Check if a file exists and can be accessed.

        Args:
            writable: If True, check if the file is writable.

        Returns:
            True if the file exists and can be accessed, False otherwise.
        """
        file_path = self.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if writable:
            file_path.touch()
        else:
            if not file_path.exists():
                return False
            if not file_path.stat().st_size:
                return False
            with file_path.open():
                pass
        return True

    def save(self, data):
        self.check_file(writable=True)
        with self.file_path.open("w") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    def load(self):
        if not self.check_file(writable=False):
            return self._LOAD_TYPE()
        with self.file_path.open() as file:
            return json.load(file)


class BoardInfoConfig(_ConfigFile):
    """Class for handling the board info configuration.

    The board info configuration is a JSON file containing a dictionary
    with the board name as key and a list of features provided by the
    board as value.

    The board info configuration file is located in the config directory
    and is named board_info.json.

    Args:
        config_dir: Directory for the configuration files.

    Attributes:
        file_path (Path): Path to the board info configuration file.
    """

    _FILENAME = "board_info.json"
    _LOAD_TYPE = dict

    def save(self, data: Dict[str, Union[str, int]]):
        """Save the board info configuration.

        Args:
            data: The board info data to save.
        """
        return super().save(data)

    def load(self) -> Dict[str, Union[str, int]]:
        """Load the board info configuration.

        Returns:
            The loaded board info data.
        """
        return super().load()


class NodesConfig(_ConfigFile):
    """Class for handling the nodes configuration.

    The nodes configuration is a JSON file containing a list of
    NmNode objects.

    The nodes configuration file is located in the config directory
    and is named nodes.json.

    Args:
        config_dir: Directory for the configuration files.

    Attributes:
        file_path (Path): Path to the nodes configuration file.
    """

    _FILENAME = "nodes.json"
    _LOAD_TYPE = list

    def save(self, data: List[NmNode]):
        """Save the nodes configuration.

        Args:
            data: The nodes data to save.
        """
        data = [node.to_dict() for node in data]
        return super().save(data)

    def load(self) -> List[NmNode]:
        """Load the nodes configuration.

        Returns:
            The loaded nodes data.
        """
        data = super().load()
        return [NmNode.from_dict(item) for item in data]


def get_default_path() -> Path:
    """
    Return the default path for the configuration files.

    Returns:
        Path: The default path for the configuration files.
    """
    return Path(os.environ.get("NM_CONFIG_DIR", "~/.config/inet_nm")).expanduser()


def config_arg(parser: argparse.ArgumentParser):
    """
    Add a configuration argument to the provided parser.

    Args:
        parser (argparse.ArgumentParser): ArgumentParser object.
    """
    parser.add_argument(
        "-c",
        "--config",
        default=get_default_path(),
        help="Path to the config dir, defaults to NM_CONFIG_DIR or "
        "~/.config/inet_nm if NM_CONFIG_DIR is not set",
    )
