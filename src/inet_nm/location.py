from typing import Dict, List

import inet_nm.usb_ctrl as ucl
from inet_nm.data_types import NmNode


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
