"""Pytest module for testing all runner apps."""
from typing import List
from unittest.mock import patch

import pytest

from inet_nm.data_types import NmNode
from inet_nm.locking import get_locked_uids
from inet_nm.runner_apps import NmShellRunner, NmTmuxPanedRunner, NmTmuxWindowedRunner


def _nodes(amount=1) -> List[NmNode]:
    nodes = []
    for i in range(1, amount + 1):
        nodes.append(
            NmNode(
                serial=f"serial{i}",
                vendor_id="vendor_id",
                product_id="product_id",
                vendor="vendor",
                model="model",
                driver="driver",
                board="board",
                features_provided=["feature0", f"feature{i}"],
            )
        )
    return nodes


def test_NmShellRunner():
    """Test default script running on dummy nodes."""
    nodes = _nodes(2)
    with NmShellRunner(nodes) as runner:
        runner.run()
    uids = get_locked_uids()
    assert nodes[0].uid not in uids
    assert nodes[1].uid not in uids


@pytest.mark.parametrize("tmux_runner", [NmTmuxPanedRunner, NmTmuxWindowedRunner])
def test_NmTmuxRunner(tmux_runner):
    """Mock tmux calls."""
    node = _nodes(1)[0]
    with patch("subprocess.run"):
        with tmux_runner([node]) as runner:
            runner.run()
    uids = get_locked_uids()
    assert node.uid not in uids
