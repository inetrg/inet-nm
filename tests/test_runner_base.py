from threading import Thread
from typing import Dict
from unittest.mock import patch

import pytest

from inet_nm.data_types import NmNode
from inet_nm.runner_base import NmNodesRunner


class MockNmNodesRunner(NmNodesRunner):
    def func(self, node: NmNode, idx: int, env: Dict[str, str]):
        return True


@pytest.fixture
def dummy_nodes():
    node1 = NmNode(
        serial="1",
        vendor="vendor1",
        product_id="product1",
        vendor_id="vendor_id1",
        model="model1",
        driver="driver1",
        board="board1",
    )
    node2 = NmNode(
        serial="2",
        vendor="vendor2",
        product_id="product2",
        vendor_id="vendor_id2",
        model="model2",
        driver="driver2",
        board="board2",
    )
    return [node1, node2]


def test_acquire_and_release(dummy_nodes):
    runner = MockNmNodesRunner(nodes=dummy_nodes)

    with patch.object(runner.locks[0], "acquire") as mock_acquire:
        with patch.object(runner.locks[0], "release") as mock_release:
            runner.acquire()
            mock_acquire.assert_called_once()

            runner.release()
            mock_release.assert_called_once()


def test_run_without_acquire(dummy_nodes):
    runner = MockNmNodesRunner(nodes=dummy_nodes)

    with pytest.raises(Exception):
        runner.run()


def test_run_with_acquire(dummy_nodes):
    runner = MockNmNodesRunner(nodes=dummy_nodes)
    runner.acquire()

    with patch.object(Thread, "start") as mock_start, patch.object(
        Thread, "join"
    ) as mock_join:
        runner.run()
        assert mock_start.call_count == len(dummy_nodes)
        assert mock_join.call_count == len(dummy_nodes)
