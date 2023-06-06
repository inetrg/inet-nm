from pathlib import Path

import pytest

from inet_nm.data_types import NmNode
from inet_nm.filelock import FileLock
from inet_nm.locking import get_lock_path, get_locked_uids, locks_dir, release_all_locks


@pytest.fixture
def dummy_nodes():
    """Return a list of dummy nodes."""
    node1 = NmNode(
        serial="1",
        vendor="vendor1",
        product_id="product1",
        vendor_id="vendor_id1",
        model="model1",
        driver="driver1",
    )
    node2 = NmNode(
        serial="2",
        vendor="vendor2",
        product_id="product2",
        vendor_id="vendor_id2",
        model=None,
        driver="driver2",
    )
    return [node1, node2]


def setup_function():
    nodes = [
        NmNode(
            serial="1",
            vendor="vendor1",
            product_id="product1",
            vendor_id="vendor_id1",
            model="model1",
            driver="driver1",
        ),
        NmNode(
            serial="2",
            vendor="vendor2",
            product_id="product2",
            vendor_id="vendor_id2",
            model=None,
            driver="driver2",
        ),
    ]

    FileLock(str(get_lock_path(nodes[0]))).acquire()
    FileLock(str(get_lock_path(nodes[1]))).acquire()


def teardown_function():
    release_all_locks()


def test_locks_dir():
    """Checks that the dir is a dir..."""
    dir_path = locks_dir()
    assert dir_path.is_dir()


def test_get_locked_uids():
    """Verify the uids are corrected in the config dir."""
    locked_uids = get_locked_uids()
    assert isinstance(locked_uids, list)
    assert len(locked_uids) == 2
    assert "460e1ae2f9c8315c74015d608e5204a6" in locked_uids
    assert "5de815ec154c80e5af83781cf36acf21" in locked_uids


def test_get_lock_path(dummy_nodes):
    """Verify lock path is correct."""
    node = dummy_nodes[0]
    lock_path = get_lock_path(node)
    assert isinstance(lock_path, Path)
    assert lock_path.name == f"{node.uid}.lock"


def test_release_all_locks():
    """Test if all locks released."""
    locked_uids = get_locked_uids()
    assert len(locked_uids) != 0
    release_all_locks()
    locked_uids = get_locked_uids()
    assert len(locked_uids) == 0
