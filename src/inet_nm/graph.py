"""Graph module for the inet_nm package.

This module provides a simple implementation of a graph data structure.
"""


def filter_valid_locations(locations):
    """Filter a list of locations into valid and invalid locations.

    Args:
        locations: List of location strings.

    Returns:
        A tuple of valid and invalid locations.

    Examples:
        locations: ['1.1.1', '3.1.2', '1.3.4', 'garbage']
        valid_locs: [(1, 1, 1), (3, 1, 2), (1, 3, 4)]
        invalid_locs: ['garbage']
    """

    valid_locs = []
    invalid_locs = []

    for loc in locations:
        parts = loc.split(".")
        if (
            len(parts) == 3
            and all(p.isdigit() for p in parts)
            and 1 <= int(parts[2]) <= 4
        ):
            valid_locs.append((int(parts[0]), int(parts[1]), int(parts[2])))
        else:
            invalid_locs.append(loc)

    return valid_locs, invalid_locs


def _get_dimensions(locations):
    if len(locations) == 0:
        return 0, 0
    max_y = max([loc[0] for loc in locations])
    max_x = max([loc[1] for loc in locations])
    return max_y, max_x


def _generate_grid(rows, cols):
    if rows == 0 or cols == 0:
        return []
    # Create a matrix to hold the data
    matrix = [[" " for _ in range(2 * cols + 1)] for _ in range(5 * rows + 1)]

    # Fill in the horizontal and vertical bars
    for i in range(5 * rows + 1):
        for j in range(2 * cols + 1):
            # For the corners and intersections
            if i % 5 == 0:
                if j % 2 == 0:
                    if (i == 0 and j == 0) or (i == 5 * rows and j == 0):
                        matrix[i][j] = "┌" if i == 0 else "└"
                    elif (i == 0 and j == 2 * cols) or (
                        i == 5 * rows and j == 2 * cols
                    ):
                        matrix[i][j] = "┐" if i == 0 else "┘"
                    else:
                        matrix[i][j] = "┬" if i == 0 else "┴" if i == 5 * rows else "┼"
            elif i % 5 != 0:
                if j % 2 == 0:
                    matrix[i][j] = "│"
            if j % 2 != 0 and i % 5 == 0:
                matrix[i][j] = "─"

    return matrix


def _overlay_locations(matrix, locations):
    for loc in locations:
        y, x, pos = loc

        matrix_len = len(matrix)
        matrix[matrix_len - ((y - 1) * 5 + pos + 1)][2 * (x - 1) + 1] = "x"


def _parse_grid(matrix):
    grid = ""
    for row in matrix:
        grid += "".join(row)
        grid += "\n"
    return grid


def parse_locations(locations):
    """Parse a list of locations into a grid string.

    Args:
        locations: List of locations to parse.

    Returns:
        A grid string representing the locations.

    Examples:
        locations: ['1.1.1', '3.1.2', '1.3.4']
        ┌─┬─┬─┐
        │ │ │ │
        │ │ │ │
        │x│ │ │
        │ │ │ │
        ┼─┼─┼─┼
        │ │ │ │
        │ │ │ │
        │ │ │ │
        │ │ │ │
        ┼─┼─┼─┼
        │ │ │x│
        │ │ │ │
        │ │ │ │
        │x│ │ │
        └─┴─┴─┘
    """
    if len(locations) == 0:
        return ""
    valid_locs, invalid_locs = filter_valid_locations(locations)
    rows, cols = _get_dimensions(valid_locs)
    grid = _generate_grid(rows, cols)
    _overlay_locations(grid, valid_locs)
    grid = _parse_grid(grid)
    return grid + "\n".join(invalid_locs)


# locs = [
#     ["1.1.1", "3.1.2", "1.3.4", "garbage"],
#     [],
#     ["1.1.1", "3.2.2", "1.3.4", "1.2.3.4"],
#     ["1.1.1", "3.1.2", "1.3.4", "1.2.6"],
#     ["1.1.1", "3.1.2", "1.3.4", "a.3.4"],
#     ["1.1.1"],
#     ["3.3.1"],
#     ["3.3.3"],
#     ["2.3.4"],
# ]
# for loc in locs:
#     print(loc)
#     print(parse_locations(loc))
#     print("==================")
