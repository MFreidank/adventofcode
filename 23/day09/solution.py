from collections import deque
from enum import Enum
from pathlib import Path
import typing

import numpy as np


class FillDirection(Enum):
    """Direction to fill in difference values. Part 1: forwards, Part 2: backwards."""
    FORWARD = "forward"
    BACKWARD = "backward"


def generate_inputs(filepath: Path) -> typing.Iterable[np.ndarray]:
    """Generate input history arrays as numpy arrays.

    Parameters:
    -----------
    filepath (pathlib.Path):
        Path to input file to read history arrays from.

    Yields:
    --------
    history_array (numpy.ndarray):
        Single history array to fill in.
    """
    with open(filepath) as f:
        for line in f:
            yield np.asarray(tuple(map(int, line.strip().split())))


def history_value(
    history: np.ndarray, fill_direction: FillDirection = FillDirection.FORWARD
) -> int:
    """Compute a history value for a given history, filling in variables in the given direction.

    Parameters:
    -----------
    history (numpy.ndarray):
        History array to fill in differences for.

    fill_direction (FillDirection):
        Direction to process array in, either `FillDirection.FORWARD` (part 1) or `FillDirection.BACKWARD` (part 2).

    Returns:
    --------
    history_value (int):
        History value for the given input history.
    """
    """"""
    history_lines = [history]

    differences = np.asarray(history)

    while True:
        differences = np.diff(differences)

        history_lines.append(differences)
        if (differences == 0).all():
            break

    accumulator = 0

    history_deque = deque(history_lines)

    while history_deque:
        if fill_direction is FillDirection.FORWARD:
            history = history_deque.popleft()
            accumulator += history[-1]
        elif fill_direction is FillDirection.BACKWARD:
            history = history_deque.pop()
            accumulator = history[0] - accumulator
        else:
            raise NotImplementedError(f"Unsupported fill direction: {fill_direction}")
    return accumulator


def part1(filepath: Path):
    return sum(
        history_value(history, fill_direction=FillDirection.FORWARD)
        for history in generate_inputs(filepath)
    )


def part2(filepath):
    return sum(
        history_value(history, fill_direction=FillDirection.BACKWARD)
        for history in generate_inputs(filepath)
    )


def main():
    filepath = Path(__file__).parent.joinpath("data", "data.txt")

    print("PART 1:", part1(filepath))
    print("PART 2:", part2(filepath))


if __name__ == "__main__":
    main()
