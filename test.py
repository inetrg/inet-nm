def filter_valid_locations(locations):
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


def get_dimensions(locations):
    max_y = max([loc[0] for loc in locations])
    max_x = max([loc[1] for loc in locations])
    return max_y, max_x


def generate_grid(rows, cols):
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


def overlay_locations(matrix, locations):
    for loc in locations:
        y, x, pos = loc
        matrix_len = len(matrix)
        matrix[matrix_len - (y * 5 - pos)][2 * (x - 1) + 1] = "x"


def print_grid(matrix, invalid_locations):
    for row in matrix:
        print("".join(row))
    for loc in invalid_locations:
        print(loc)


def print_locations(locations):
    if len(locations) == 0:
        print("No locations found")
        return
    valid_locs, invalid_locs = filter_valid_locations(locations)
    rows, cols = get_dimensions(valid_locs)
    grid = generate_grid(rows, cols)
    overlay_locations(grid, valid_locs)
    print_grid(grid, invalid_locs)


locs = [
    ["1.1.1", "3.1.2", "1.3.4", "garbage"],
    [],
    ["1.1.1", "3.1.2", "1.3.4", "1.2.3.4"],
    ["1.1.1", "3.1.2", "1.3.4", "1.2.6"],
    ["1.1.1", "3.1.2", "1.3.4", "a.3.4"],
    ["1.1.1"],
    ["3.3.1"],
]
for loc in locs:
    print(loc)
    print_locations(loc)
    print("==================")
