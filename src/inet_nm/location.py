from typing import Dict, List

import inet_nm.usb_ctrl as ucl
from inet_nm.data_types import NmNode


def merge_location_cache_chunks(caches: List[List[Dict]]):
    """
    Merge location cache chunks into a single cache.

    Due to only being able to power on a chunk at a time we need to sort
    through each of the location caches and look through all id_paths that
    have a missing state and see if they are available in another chunk.
    If they are then probably they were just powered off.

    Args:
        caches: List of location cache chunks.

    Returns:
        The merged location cache.
    """
    # TODO: Also check if all id_paths that are attached have the same node_uid
    tmp_cache = {}
    for chunk in caches:
        for entry in chunk:
            # If entry is empty, skip it
            if not entry:
                continue
            if entry["state"] != "missing":
                tmp_cache[entry["id_path"]] = entry
                continue
            if entry["state"] == "missing" and entry["id_path"] not in tmp_cache:
                tmp_cache[entry["id_path"]] = entry
    # Convert tmp_cache to list
    cache = list(tmp_cache.values())
    cache.sort(key=lambda x: x["id_path"])
    return cache


def get_location_cache(nodes: List[NmNode], id_paths: Dict):
    """
    Get the location cache for a list of NmNode objects.

    Args:
        nodes: List of NmNode objects.
        id_paths: List of id_paths to check.

    Returns:
        The location cache.
    """
    processed_id_paths = set()
    cache = []
    node_uids = {node.uid for node in nodes if not node.ignore}
    for id_path in id_paths:
        node_uid = ucl.get_uid_from_id_path(id_path)
        if node_uid is not None and node_uid in node_uids:
            cache.append(
                {"id_path": id_path, "node_uid": node_uid, "state": "attached"}
            )
        else:
            cache.append({"id_path": id_path, "node_uid": node_uid, "state": "missing"})
        processed_id_paths.add(id_path)

    for node in nodes:
        try:
            id_path = ucl.get_id_path_from_node(node)
            if id_path not in processed_id_paths:
                cache.append(
                    {"id_path": id_path, "node_uid": node.uid, "state": "unassigned"}
                )
                processed_id_paths.add(id_path)
        except Exception:
            pass
    cache.sort(key=lambda x: x["id_path"])
    return cache
