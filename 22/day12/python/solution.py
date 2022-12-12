from collections import deque
import math
from pathlib import Path
import typing


def get_heightmap(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.List[str]:
    """Return heightmap, rows are lists.
       Each element is a string containing the columnwise elevation letters of the row.

    Parameters
    ----------
    filepath: pathlib.Path, optional
        Path to advent of code input file.

    Returns
    -------
    heightmap: typing.List[str]
       Each element is a string containing the columnwise elevation letters of a row.
    """
    with open(filepath) as inputs_file:
        heightmap = inputs_file.read().splitlines()

    return heightmap


def positions_with_elevation_letter(
    heightmap: typing.List[str],
    elevation_letter: str,
) -> typing.List[typing.Tuple[int, int]]:
    """Retrieve row and column indices for all occurrences of a given elevation
       letter in the heightmap.

    Parameters
    ----------
    heightmap : typing.List[str]
        Heightmap, where each list element is a string containing the columnwise
        elevation letters of a row.
    elevation_letter : str
        Elevation letter to retrieve positions for.

    Returns
    -------
    positions: typing.List[typing.Tuple[int, int]]
        Each list element is a tuple `(row_index, column_index)` where
        `heightmap[row_index][column_index] == elevation_letter`.
    """
    num_rows, num_columns = len(heightmap), len(heightmap[0])

    return [
        (row_index, column_index)
        for row_index in range(num_rows)
        for column_index in range(num_columns)
        if heightmap[row_index][column_index] == elevation_letter
    ]


def height_at_position(
    heightmap: typing.List[str], row_index: int, column_index: int
) -> int:
    """Return integer height corresponding to a given row and column index.

    Parameters
    ----------
    heightmap : typing.List[str]
        Heightmap, where each list element is a string containing the columnwise
        elevation letters of a row.
    row_index : int
        Index of the heightmap row to retrieve.
    column_index : int
        Index of the heightmap column to retrieve.

    Returns
    -------
    height: int
        Integer height value at the given index.
    """
    letter_at_position = str(heightmap[row_index][column_index])

    # NOTE: Special cases; "S" is the start and always has elevation "a" and
    # "E" is the goal and always has elevation "z".
    if letter_at_position == "S":
        letter_at_position = "a"
    elif letter_at_position == "E":
        letter_at_position = "z"

    return ord(letter_at_position)


def breadth_first_height_search(
    heightmap: typing.List[str],
    start_position_index: typing.Tuple[int, int],
    goal_position_index: typing.Tuple[int, int],
) -> int:
    """Determine number of steps from a given start to goal position, by
       using breadth first search and determining neighbording nodes to expand
       using a heightmap to ensure elevation increases never exceed 1 in one step.

    Parameters
    ----------
    heightmap : typing.List[str]
        Heightmap, where each list element is a string containing the columnwise
        elevation letters of a row.
    start_position_index : typing.Tuple[int, int]
        Tuple of row and column index to start search from.
    goal_position_index : typing.Tuple[int, int]
        Tuple of row and column index that indicates the goal of the search.

    Returns
    -------
    num_steps: int
       Minimal number of steps needed from the start to the goal node.
    """
    num_rows, num_columns = len(heightmap), len(heightmap[0])

    start_row_index, start_column_index = start_position_index
    goal_row_index, goal_column_index = goal_position_index

    steps = [[math.inf] * num_columns for _ in range(num_rows)]
    steps[start_row_index][start_column_index] = 0

    index_queue = deque([(start_row_index, start_column_index)])

    while index_queue:
        current_row_index, current_column_index = index_queue.popleft()

        for step_row_offset, step_column_offset in (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ):
            new_row_index, new_column_index = (
                current_row_index + step_row_offset,
                current_column_index + step_column_offset,
            )
            if (
                (0 <= new_row_index < num_rows)
                and (0 <= new_column_index < num_columns)
                and (steps[new_row_index][new_column_index] == math.inf)
                and (
                    height_at_position(
                        heightmap=heightmap,
                        row_index=new_row_index,
                        column_index=new_column_index,
                    )
                    <= (
                        height_at_position(
                            heightmap=heightmap,
                            row_index=current_row_index,
                            column_index=current_column_index,
                        )
                        + 1
                    )
                )
            ):
                steps[new_row_index][new_column_index] = (
                    steps[current_row_index][current_column_index] + 1
                )
                index_queue.append((new_row_index, new_column_index))

    return steps[goal_row_index][goal_column_index]


def part_1(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> int:
    """Minimum number of steps needed from a given start position ("S") to the given goal position ("E").

    Parameters
    ----------
    filepath: pathlib.Path, optional
        Path to advent of code input file.

    Returns
    -------
    num_steps: int
       Minimal number of steps needed from the start ("S") to the goal ("E") position.
    """
    heightmap = get_heightmap()
    (start_position_index,) = positions_with_elevation_letter(
        heightmap=heightmap, elevation_letter="S"
    )
    (goal_position_index,) = positions_with_elevation_letter(
        heightmap=heightmap, elevation_letter="E"
    )

    return breadth_first_height_search(
        heightmap=heightmap,
        start_position_index=start_position_index,
        goal_position_index=goal_position_index,
    )


def part_2(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> int:
    """Minimum number of steps needed when starting from any position with elevation "a"
       to the given goal position ("E").

    Parameters
    ----------
    filepath: pathlib.Path, optional
        Path to advent of code input file.

    Returns
    -------
    num_steps: int
       Minimal number of steps needed when starting from any position with elevation "a"
       to the given goal position ("E").

    """
    heightmap = get_heightmap()

    start_position_indices = positions_with_elevation_letter(
        heightmap=heightmap, elevation_letter="a"
    )
    (goal_position_index,) = positions_with_elevation_letter(
        heightmap=heightmap, elevation_letter="E"
    )

    return min(
        breadth_first_height_search(
            heightmap=heightmap,
            start_position_index=start_position_index,
            goal_position_index=goal_position_index,
        )
        for start_position_index in start_position_indices
    )


def main():
    print("Part 1:", part_1())
    print("Part 2:", part_2())


if __name__ == "__main__":
    main()
