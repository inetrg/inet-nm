"""This module contains functions for locking nodes."""
import os
import tempfile
from pathlib import Path
from typing import List

from inet_nm.data_types import NmNode


def locks_dir() -> Path:
    """
    Get the directory for lock files.

    If the directory does not exist, create it.

    Returns:
        The path to the lock files directory.
    """
    path = Path(tempfile.gettempdir(), "inet_nm", "locks")
    os.umask(0)
    path.mkdir(parents=True, exist_ok=True, mode=0o777)
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
