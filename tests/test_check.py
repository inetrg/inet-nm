from unittest.mock import patch

import pytest

from inet_nm.check import (
    check_nodes,
    eval_features,
    filter_nodes,
    filter_used_nodes,
    get_all_features,
    skip_duplicate_boards,
)
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
        features_provided=["feature1", "feature2"],
        board="board1",
    )
    node2 = NmNode(
        serial="2",
        vendor="vendor2",
        product_id="product2",
        vendor_id="vendor_id2",
        model="model2",
        driver="driver2",
        features_provided=["feature1"],
        board="board2",
    )
    node3 = NmNode(
        serial="3",
        vendor="vendor3",
        product_id="product3",
        vendor_id="vendor_id3",
        model="model3",
        driver="driver3",
        features_provided=["feature2", "feature3"],
        board="board3",
    )
    node4 = NmNode(
        serial="4",
        vendor="vendor4",
        product_id="product4",
        vendor_id="vendor_id4",
        model="model4",
        driver="driver4",
        features_provided=["feature2", "feature4"],
        board="board3",
    )
    return [node1, node2, node3, node4]


@pytest.fixture
def locked_nodes(dummy_nodes):
    """Return a list of locked nodes."""
    return [dummy_nodes[0].uid, dummy_nodes[1].uid]


def test_get_all_features(dummy_nodes):
    """Ensure all features are captured from the dummy nodes."""
    features = get_all_features(dummy_nodes)
    assert features == set(["feature1", "feature2", "feature3", "feature4"])


def test_filter_nodes(dummy_nodes):
    """Ensure nodes are filtered correctly using feature filter."""
    nodes = filter_nodes(dummy_nodes, ["feature1"])
    assert len(nodes) == 2
    assert nodes[0].serial == "1"
    assert nodes[1].serial == "2"


def test_skip_duplicate_boards(dummy_nodes):
    """Ensure nodes with duplicate boards are skipped."""
    nodes = skip_duplicate_boards(dummy_nodes)
    assert len(nodes) == 3
    assert nodes[0].serial == "1"
    assert nodes[1].serial == "2"
    assert nodes[2].serial == "3"


@patch("inet_nm.check.get_connected_uids")
def test_check_nodes(mock_get_connected_uids, dummy_nodes):
    """Mock the connected nodes are being captured"""
    mock_get_connected_uids.return_value = [
        dummy_nodes[0].uid,
        dummy_nodes[1].uid,
        dummy_nodes[2].uid,
    ]
    nodes = check_nodes(dummy_nodes)
    assert len(nodes) == 3


def test_filter_used_nodes(dummy_nodes, locked_nodes):
    """Ensure locked nodes are removed from the list of nodes."""
    nodes = filter_used_nodes(dummy_nodes, locked_nodes, remove=True)
    assert len(nodes) == 2
    assert nodes[0].serial == "3"
    assert nodes[1].serial == "4"

    nodes = filter_used_nodes(dummy_nodes, locked_nodes, remove=False)
    assert len(nodes) == 2
    assert nodes[0].serial == "1"
    assert nodes[1].serial == "2"


def test_eval_features(dummy_nodes):
    """Ensure nodes are filtered correctly using eval feature."""
    features = get_all_features(dummy_nodes)
    nodes = eval_features(
        dummy_nodes, features, "(feature3 and feature2) or (feature1 and not feature2)"
    )
    assert len(nodes) == 2
    assert nodes[0].serial == "2"
    assert nodes[1].serial == "3"
