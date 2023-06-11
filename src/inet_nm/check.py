"""
This module contains functions for checking the state of the boards.

This is meant for evaluating inventory.
"""
import argparse
import json
from typing import Dict, List

import pyudev

import inet_nm.config as cfg
from inet_nm.data_types import NmNode
from inet_nm.locking import get_locked_uids


def get_connected_uids() -> List[str]:
    """
    Get the UIDs of all connected USB devices.

    Returns:
        A list of UIDs of all connected USB devices.
    """
    uids = []
    context = pyudev.Context()
    for device in context.list_devices(subsystem="tty"):
        parent = device.find_parent("usb", "usb_device")
        if parent is None:
            continue
        vendor_id = parent.get("ID_VENDOR_ID")
        model_id = parent.get("ID_MODEL_ID")
        serial_short = parent.get("ID_SERIAL_SHORT")
        uids.append(NmNode.calculate_uid(model_id, vendor_id, serial_short))
    return uids


def get_nodes_with_state(nodes: List[NmNode], connected=True) -> List[NmNode]:
    """
    Get a list of nodes that are connected or not connected.

    Args:
        nodes: A list of nodes to filter.
        connected: If True, return the nodes that are
            connected. If False, return the nodes that are not connected.

    Returns:
        A list of filtered nodes.
    """
    selected_nodes = []
    connected_uids = get_connected_uids()
    for node in nodes:
        if node.uid in connected_uids:
            if connected:
                selected_nodes.append(node)
        elif not connected:
            selected_nodes.append(node)
    return selected_nodes


def remove_used_nodes(nodes: List[NmNode], used_uids: List[str]) -> List[NmNode]:
    """
    Remove the nodes that are already used from the list of nodes.

    Args:
        nodes: A list of nodes to filter.
        used_uids: A list of UIDs of nodes that are already used.

    Returns:
        List[NmNode]: A list of nodes that are not already used.
    """
    if used_uids is None:
        used_uids = []
    selected_nodes = []
    for node in nodes:
        if node.uid not in used_uids:
            selected_nodes.append(node)
    return selected_nodes


def filter_nodes(nodes: List[NmNode], must_contain: List[str]) -> List[NmNode]:
    """
    Filter the nodes based on the provided features.

    Args:
        nodes: A list of nodes to filter.
        must_contain: A list of features. Only the nodes that contain all of
            these features will be returned.

    Returns:
        A list of filtered nodes.
    """
    selected_nodes = []
    for node in nodes:
        if all([feature in node.features_provided for feature in must_contain]):
            selected_nodes.append(node)
    return selected_nodes


def nodes_to_boards(nodes: List[NmNode]) -> Dict[str, int]:
    """
    Convert a list of nodes to a dictionary of board counts.

    Args:
        nodes: A list of nodes.

    Returns:
        A dictionary where the keys are the names of the boards and the values
            are the counts of those boards.
    """
    boards = {}
    for node in nodes:
        if node.board not in boards:
            boards[node.board] = 0
        boards[node.board] += 1
    return boards


def get_all_features(nodes: List[NmNode]) -> List[str]:
    """
    Get a list of all features provided by the nodes.

    Args:
        nodes: A list of nodes.

    Returns:
        A list of all features.
    """
    features = []
    for node in nodes:
        features.extend(node.features_provided)
    return set(features)


def eval_features(nodes: List[NmNode], features: set, eval_func):
    """
    Evaluate features of nodes using a provided function.

    Args:
        nodes: A list of nodes to evaluate.
        features: A set of features to evaluate.
        eval_func: The function to use to evaluate the features.

    Returns:
        A list of nodes that meet the criteria of the evaluation function.

    Raises:
        ValueError: If the evaluation function cannot be evaluated.
    """
    selected_nodes = []
    try:
        for node in nodes:
            selected_features = {
                feature: feature in node.features_provided for feature in features
            }
            if eval(eval_func, selected_features):
                selected_nodes.append(node)
    except Exception as e:
        raise ValueError(
            f"Could not evaluate {eval_func} with {sorted(features)}"
        ) from e
    return selected_nodes


def skip_duplicate_boards(nodes: List[NmNode]) -> List[NmNode]:
    """
    Remove duplicate boards from a list of nodes.

    Args:
        nodes: A list of nodes.

    Returns:
        A list of nodes without duplicates.
    """
    selected_nodes = []
    boards = set()
    for node in nodes:
        if node.board not in boards:
            selected_nodes.append(node)
        boards.add(node.board)
    return selected_nodes


def check_nodes(
    nodes: List[NmNode],
    all_nodes: bool = False,
    missing: bool = False,
    feat_filter: List[str] = None,
    feat_eval: str = None,
    used: bool = False,
    skip_dups: bool = False,
    locked_nodes: List[str] = None,
) -> List[NmNode]:
    """
    Get a filtered list of nodes based on the provided parameters.

    Args:
        nodes: A list of nodes to check.
        all_nodes: If True, all nodes will be returned.
        missing: If True, only the nodes that are missing will be returned.
        feat_filter: A list of features. Only the nodes that contain all of
            these features will be returned.
        feat_eval: The function to use to evaluate the features.
        used: If True, used nodes will also be returned.
        skip_dups: If True, duplicate nodes will be removed.
        locked_nodes: A list of UIDs of nodes that are locked.

    Returns:
        A list of filtered nodes.
    """
    features = get_all_features(nodes)
    if not all_nodes:
        nodes = get_nodes_with_state(nodes, connected=not missing)
    if not used:
        nodes = remove_used_nodes(nodes, locked_nodes)
    if feat_filter:
        nodes = filter_nodes(nodes, feat_filter)
    if feat_eval:
        nodes = eval_features(nodes, features, feat_eval)
    if skip_dups:
        nodes = skip_duplicate_boards(nodes)
    # filter out ignored nodes
    nodes = [node for node in nodes if not node.ignore]
    return nodes


def check_args(parser: argparse.ArgumentParser):
    """
    Define the arguments for the argparse parser.

    Args:
        parser: The argparse parser.
    """
    parser.add_argument(
        "-f",
        "--feat-filter",
        nargs="+",
        help="Filter all boards that don't provide these features",
    )
    parser.add_argument(
        "-a",
        "--all-nodes",
        action="store_true",
        help="Show all boards, regardless of connection",
    )
    parser.add_argument(
        "-m", "--missing", action="store_true", help="Show all missing boards"
    )
    parser.add_argument(
        "-e", "--feat-eval", type=str, help="Evaluate features with this function"
    )
    parser.add_argument(
        "-u", "--used", action="store_true", help="Show used boards as well"
    )
    parser.add_argument(
        "-s", "--skip-dups", action="store_true", help="Skip duplicate boards"
    )


def get_filtered_nodes(
    config: str,
    all_nodes: bool = False,
    missing: bool = False,
    feat_filter: List[str] = None,
    feat_eval: str = None,
    used: bool = False,
    skip_dups: bool = False,
) -> List[NmNode]:
    """
    Get a list of nodes based on the provided parameters.

    Args:
        config: The configuration path for the nodes.
        all_nodes: If True, all nodes will be returned.
        missing: If True, only the nodes that are missing will be returned.
        feat_filter: A list of features. Only the nodes that contain all of
            these features will be returned.
        feat_eval: The function to use to evaluate the features.
        used: If True, used nodes will also be returned.
        skip_dups: If True, duplicate nodes will be removed.

    Returns:
        A list of filtered nodes.
    """
    nodes = cfg.NodesConfig(config).load()
    locked_nodes = get_locked_uids()
    nodes = check_nodes(
        nodes, all_nodes, missing, feat_filter, feat_eval, used, skip_dups, locked_nodes
    )
    return nodes


def all_features_from_nodes(nodes: List[NmNode]) -> List[str]:
    """
    Get a list of all features provided by the nodes.

    Args:
        nodes: A list of nodes.

    Returns:
        A list of all features.
    """
    features = []
    for node in nodes:
        features.extend(node.features_provided)
    return sorted(list(set(features)))


def cli_count_board_inventory():
    """CLI entrypoint for counting the inventory of boards."""
    parser = argparse.ArgumentParser(description="Check the state of the boards")
    cfg.config_arg(parser)
    check_args(parser)
    parser.add_argument(
        "--show-features", action="store_true", help="Shows all features for all boards"
    )
    args = parser.parse_args()
    kwargs = vars(args)
    show_features = kwargs.pop("show_features")

    nodes = get_filtered_nodes(**kwargs)

    if show_features:
        info = all_features_from_nodes(nodes)
    else:
        info = nodes_to_boards(nodes)
    out = json.dumps(info, indent=2, sort_keys=True)
    print(out)
