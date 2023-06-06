from copy import copy
from unittest.mock import MagicMock, patch

import pytest

import inet_nm.commissioner as commissioner
from inet_nm.data_types import NmNode


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


@pytest.fixture
def mock_devices():
    # Mock the devices returned by context.list_devices
    mock_device_1 = MagicMock()
    mock_device_1.device_node = "/dev/ttyUSB0"
    mock_device_1.find_parent.return_value.get.side_effect = [
        "vendor_id1",
        "product1",
        "1",
        "vendor1",
        "model1",
        "driver1",
    ]

    mock_device_2 = MagicMock()
    mock_device_2.device_node = "/dev/ttyUSB1"
    mock_device_2.find_parent.return_value.get.side_effect = [
        "vendor_id2",
        "product2",
        "2",
        "vendor2",
        None,
        "driver2",
    ]

    return [mock_device_1, mock_device_2]


def test_get_devices_from_tty(mock_devices, dummy_nodes):
    """Mock devices returned by context.list_devices."""
    # Mock the context.list_devices method
    list_devices_mock = MagicMock()
    list_devices_mock.return_value = mock_devices

    with patch("pyudev.Context.list_devices", list_devices_mock):
        assert commissioner.get_devices_from_tty() == dummy_nodes


def test_get_tty_from_nm_node(mock_devices, dummy_nodes):
    """Test if the tty can be checked fro a given node."""
    with patch("pyudev.Context.list_devices", MagicMock(return_value=mock_devices[:1])):
        assert (
            commissioner.get_tty_from_nm_node(dummy_nodes[0])
            == mock_devices[0].device_node
        )

        with pytest.raises(commissioner.TtyNotPresent):
            commissioner.get_tty_from_nm_node(dummy_nodes[1])


def test_add_node_to_nodes(dummy_nodes):
    """Test if a node can be added to a list of nodes."""
    nodes = copy(dummy_nodes)
    new_node = NmNode(
        vendor_id="vendor_id3",
        product_id="product3",
        serial="3",
        vendor="vendor3",
        model="model3",
        driver="driver3",
    )
    assert len(commissioner.add_node_to_nodes(nodes, new_node)) == 3
    assert len(commissioner.add_node_to_nodes(nodes, nodes[-1])) == 2

    different_old_node = copy(nodes[-1])
    different_old_node.model = "something different"
    new_nodes = commissioner.add_node_to_nodes(nodes, different_old_node)
    assert len(new_nodes) == 2
    assert new_nodes[-1].model == "something different"
