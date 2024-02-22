import pytest

import inet_nm.location as loc


@pytest.mark.parametrize(
    "caches",
    [
        [[{}]],
        [[{"id_path": "1", "node_uid": "1", "state": "attached"}]],
        [
            [
                {"id_path": "1", "node_uid": "1", "state": "attached"},
            ],
            [{"id_path": "1", "node_uid": "1", "state": "missing"}],
        ],
        [
            [
                {"id_path": "1", "node_uid": "1", "state": "unassigned"},
                {"id_path": "2", "node_uid": "2", "state": "missing"},
            ],
            [{"id_path": "2", "node_uid": "2", "state": "attached"}],
        ],
    ],
)
def test_merge_location_cache_chunks_no_missing(caches):
    cache = loc.merge_location_cache_chunks(caches)
    assert not any(entry["state"] == "missing" for entry in cache), cache


@pytest.mark.parametrize(
    "caches",
    [
        [[{"id_path": "1", "node_uid": "1", "state": "missing"}]],
        [
            [
                {"id_path": "1", "node_uid": "1", "state": "attached"},
                {"id_path": "2", "node_uid": "2", "state": "missing"},
            ],
        ],
        [
            [
                {"id_path": "1", "node_uid": "1", "state": "missing"},
            ],
            [
                {"id_path": "1", "node_uid": "1", "state": "missing"},
            ],
        ],
    ],
)
def test_merge_location_cache_chunks_missing(caches):
    cache = loc.merge_location_cache_chunks(caches)
    assert any(entry["state"] == "missing" for entry in cache), cache
