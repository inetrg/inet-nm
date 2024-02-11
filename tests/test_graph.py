import pytest

import inet_nm.graph as gra


def test_filter_valid_locations():
    locations = ["1.1.1", "3.1.2", "1.3.4", "garbage", "1.2.6"]
    valid_locs = [(1, 1, 1), (3, 1, 2), (1, 3, 4)]
    invalid_locs = ["garbage", "1.2.6"]
    assert gra.filter_valid_locations(locations) == (valid_locs, invalid_locs)


def test_parse_locations_basic():
    locations = ["1.1.1"]
    grid = """\
┌─┐
│ │
│ │
│ │
│x│
└─┘
"""
    assert gra.parse_locations(locations) == grid


def test_parse_locations_empty():
    locations = []
    grid = ""
    assert gra.parse_locations(locations) == grid


def test_parse_locations_advanced():
    locations = ["2.3.4", "1.2.3", "1.1.5", "garbage", "1.1"]
    grid = """\
┌─┬─┬─┐
│ │ │x│
│ │ │ │
│ │ │ │
│ │ │ │
┼─┼─┼─┼
│ │ │ │
│ │x│ │
│ │ │ │
│ │ │ │
└─┴─┴─┘
1.1.5
garbage
1.1\
"""
    assert gra.parse_locations(locations) == grid


@pytest.mark.parametrize(
    "data",
    [
        ["1.1.1", "3.1.2", "1.3.4", "garbage"],
        [],
        ["1.1.1", "3.2.2", "1.3.4", "1.2.3.4"],
        ["1.1.1", "3.1.2", "1.3.4", "1.2.6"],
        ["1.1.1", "3.1.2", "1.3.4", "a.3.4"],
        ["1.1.1"],
        ["3.3.1"],
        ["3.3.3"],
        ["2.2.2"],
    ],
)
def test_get_dimensions(data):
    print(gra.parse_locations(data))
