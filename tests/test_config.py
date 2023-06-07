import pytest

from inet_nm.config import (
    get_lock_path,
    load_board_info,
    load_nodes,
    save_board_info,
    save_nodes,
)
from inet_nm.data_types import NmNode


def test_save_load_board_info(tmp_path):
    """Test saving and loading the riot board info."""
    board_info = {"board": "riot", "version": "1.0"}
    save_board_info(tmp_path, board_info)
    loaded_board_info = load_board_info(tmp_path)
    assert loaded_board_info == board_info
    assert len(load_board_info("does_not_exist")) == 0


@pytest.mark.parametrize(
    "nodes_data",
    [
        [],
        [
            {
                "serial": "1",
                "vendor_id": "vendor_id1",
                "product_id": "product1",
                "vendor": "vendor1",
                "model": "model1",
                "driver": "driver1",
            }
        ],
    ],
)
def test_save_load_nodes(tmp_path, nodes_data):
    """Test saving and loading the nodes."""
    nodes = [NmNode.from_dict(data) for data in nodes_data]
    save_nodes(tmp_path, nodes)
    loaded_nodes = load_nodes(tmp_path)
    assert loaded_nodes == nodes
    assert len(load_nodes("does_not_exist")) == 0


def test_get_lock_path(tmp_path):
    """Test getting the lock path."""
    lock_path = get_lock_path(tmp_path)
    assert lock_path == tmp_path / "locks"
