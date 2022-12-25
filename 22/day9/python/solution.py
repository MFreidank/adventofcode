from enum import Enum
from pathlib import Path
import typing

import numpy as np

GRID_DIMENSIONS = {
    "num_rows": 5,
    "num_columns": 6,
}


class Direction(Enum):
    """Enumeration of valid direction specifications."""

    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"

    @classmethod
    def from_string(cls, direction_str: str):
        """Convert string direction to enum type.

        Parameters
        ----------
        direction_str: str
            String representation of the direction to move into.

        Returns
        -------
        direction_enum: Direction
            Enum type that corresponds to `direction_str`.
        """
        match direction_str:
            case "U":
                return cls.UP
            case "D":
                return cls.DOWN
            case "L":
                return cls.LEFT
            case "R":
                return cls.RIGHT
            case _:
                raise ValueError(
                    f"Encountered unsupported direction string input '{direction_str}'."
                )


def generate_instructions(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[typing.Tuple[Direction, int]]:
    """Generates instructions consisting of tuples of a direction with corresponding number of steps.

    Parameters:
    -----------
    filepath: Path, optional
        Path to an input file.

    Yields:
    -------
    instructions: typing.Tuple[Direction, int]
        Instruction tuple consisting of a direction and an integer step size.
    """
    with open(filepath) as f:
        for line in f:
            direction_str, num_steps = line.strip().split(" ")

            yield Direction.from_string(direction_str), int(num_steps)


def move_head(direction: Direction, current_position: np.ndarray) -> np.ndarray:
    """Move the head knot one step in the given direction.

    Parameters
    ----------
    direction : Direction
        Direction to move into.
    current_position : np.ndarray
        Position of the head knot prior to the step.

    Returns
    -------
    new_head_position: np.ndarray
        Position of the head knot after taking the step.
    """
    match direction:
        case Direction.UP:
            return current_position + np.asarray([-1, 0])
        case Direction.DOWN:
            return current_position + np.asarray([1, 0])
        case Direction.RIGHT:
            return current_position + np.asarray([0, 1])
        case Direction.LEFT:
            return current_position + np.asarray([0, -1])
        case _:
            raise ValueError(
                f"Encountered unsupported direction enum input '{direction}'."
            )


def adjust_tail(head_position: np.ndarray, tail_position: np.ndarray) -> np.ndarray:
    """Adjust the tail after moving the head to `head_position`.

    Parameters
    ----------
    head_position : np.ndarray
        Head position to correspondigly adjust the tail to.
    tail_position : np.ndarray
        Tail position prior to adjustment step.

    Returns
    -------
    new_tail_position: np.ndarray
        Tail position after adjustment.
    """
    difference = head_position - tail_position
    row_difference, col_difference = difference[0], difference[1]
    if (abs(row_difference) <= 1) and (abs(col_difference) <= 1):
        # NOTE: No adjustment needed, we're still adjacent
        return tail_position

    row_change, col_change = 0, 0

    # NOTE: Ensure step length is always either 0, 1 or -1 in both row and column
    # direction. Simply divide by absolute value when difference is not 0.
    if row_difference != 0:
        row_change = row_difference // abs(row_difference)

    if col_difference != 0:
        col_change = col_difference // abs(col_difference)

    return tail_position + np.asarray([row_change, col_change])


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    knot_starting_position: np.ndarray = np.asarray(
        (GRID_DIMENSIONS["num_rows"] - 1, 0)
    ),
) -> int:
    """Solve the problem for n=2 knots, one head knot and one tail knot.

    Parameters:
    -----------
    filepath: Path, optional
        Path to an input file to read instructions from.
    knot_starting_position: np.ndarray, optional
        Starting position of the knots. Defaults to the lower left corner of the grid.

    Returns:
    --------
    num_visited_tail_positions: int
        Number of unique positions visited by the tail while processing instructions.
    """
    current_head_position = np.asarray(knot_starting_position)
    current_tail_position = np.asarray(knot_starting_position)

    visited_positions = set([tuple(current_tail_position)])

    for direction, num_steps in generate_instructions(filepath=filepath):
        for i in range(num_steps):
            current_head_position = move_head(
                direction=direction, current_position=current_head_position
            )
            current_tail_position = adjust_tail(
                head_position=current_head_position, tail_position=current_tail_position
            )

            visited_positions.add(tuple(current_tail_position))

    return len(visited_positions)


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    num_knots: int = 10,
    knot_starting_position: np.ndarray = np.asarray(
        (GRID_DIMENSIONS["num_rows"] - 1, 0)
    ),
) -> int:
    """Solve the problem for n=10 knots, one head knot and 9 tail knots each following the knot before.
       The first tail knot follows the head knot.

    Parameters:
    -----------
    filepath: Path, optional
        Path to an input file to read instructions from.
    num_knots: int, optional
        Number of knots to use. Defaults to `10` which was used in the problem.
    knot_starting_position: np.ndarray, optional
        Starting positions of the knots. Defaults to the lower left corner of the grid..

    Returns:
    --------
    num_visited_tail_positions: int
        Number of unique positions visited by the last tail while processing instructions.
    """
    knot_positions = [knot_starting_position] * num_knots

    visited_positions = set([tuple(knot_starting_position)])

    for direction, num_steps in generate_instructions(filepath=filepath):
        for i in range(num_steps):
            knot_positions[0] = move_head(
                direction=direction, current_position=knot_positions[0]
            )

            for tail_knot_id in range(1, len(knot_positions)):
                knot_positions[tail_knot_id] = adjust_tail(
                    head_position=knot_positions[tail_knot_id - 1],
                    tail_position=knot_positions[tail_knot_id],
                )

            visited_positions.add(tuple(knot_positions[-1]))

    return len(visited_positions)


def main():
    print(part_1())
    print(part_2())


if __name__ == "__main__":
    main()
