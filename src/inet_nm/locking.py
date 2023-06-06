"""This module contains functions for locking nodes."""
import tempfile
from pathlib import Path
from typing import List

from inet_nm._helpers import nm_print
from inet_nm.data_types import NmNode


def locks_dir() -> Path:
    """
    Get the directory for lock files.

    If the directory does not exist, create it.

    Returns:
        The path to the lock files directory.
    """
    path = Path(tempfile.gettempdir(), "inet_nm", "locks")
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_locked_uids() -> List[str]:
    """
    Get the list of UIDs of currently locked nodes.

    Returns:
        A sorted list of UIDs of locked nodes.
    """
    uids = [lock_file.stem for lock_file in locks_dir().glob("*.lock")]
    return sorted(uids)


def get_lock_path(node: NmNode) -> Path:
    """
    Get the path to the lock file for a given node.

    Args:
        node: The node for which to get the lock file path.

    Returns:
        The path to the lock file for the node.
    """
    return locks_dir() / f"{node.uid}.lock"


def release_all_locks():
    """Release all locks by deleting all lock files."""
    for lock_file in locks_dir().glob("*"):
        lock_file.unlink()


def cli_release_all_locks():
    """Release all locks by deleting all lock files and print the process."""
    for lock_file in locks_dir().glob("*"):
        nm_print(f"Removing lock file {lock_file}")
        lock_file.unlink()
