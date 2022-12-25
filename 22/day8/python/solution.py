from functools import reduce
from pathlib import Path
import typing

import numpy as np


def generate_trees(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[typing.List[int]]:
    """Generate a matrix of tree elevations from the input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file to read tree elevation array from.

    Yields
    ------
    tree_array: np.ndarray
        Matrix of tree elevations.
    """
    with open(filepath, "r") as f:
        for line in f:
            yield list(map(lambda number: int(number), line.strip()))


def part_1(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> int:
    """Determine number of trees visible from the outside of the tree grid.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file to read tree elevation array from.

    Returns
    -------
    visible_tree_count: int
        Number of trees visible from the outside of the tree grid.
    """
    trees = np.asarray(list(generate_trees()))
    num_rows, num_columns = len(trees), len(trees[0])

    visible_trees = 0
    for row_id in range(num_rows):
        for col_id in range(num_columns):
            tree_height = trees[row_id, col_id]
            elements_to_left = trees[row_id, :col_id]
            elements_to_right = trees[row_id, col_id + 1 :]
            elements_below = (
                trees[row_id + 1 :, col_id]
                if (row_id + 1) < num_rows
                else np.asarray([])
            )
            elements_above = trees[:row_id, col_id] if row_id > 0 else np.asarray([])

            if (
                ((elements_to_left < tree_height).all())
                or ((elements_to_right < tree_height).all())
                or ((elements_below < tree_height).all())
                or ((elements_above < tree_height).all())
            ):
                visible_trees += 1

    return visible_trees


def count_visible_trees(
    tree_array: np.ndarray,
    tree_height: int,
):
    """Count number of trees not blocked by a tree with a given height.

    Parameters
    ----------
    tree_array : np.ndarray
        2-d tree elevation matrix.
    tree_height : int
        Height of tree to use as reference.

    Returns
    -------
    visible_tree_count: int
        Number of trees not blocked by a tree with the given `tree_height`.
    """
    count = 0
    for tree in tree_array:
        if tree_height > tree:
            count += 1
        else:
            return count + 1
    return count


def scenic_score(
    tree_position: typing.Tuple[int, int],
    trees: np.ndarray,
) -> int:
    """Determine scenic score of a tree in a given tree elevation map.
       A tree's scenic score is found by multiplying together its viewing distance
       in each of the four directions.

    Parameters
    ----------
    tree_position : typing.Tuple[int, int]
        2d (row, column) coordinate index of a given tree.

    trees : np.ndarray
        2-d tree elevation matrix.

    Returns
    -------
    scenic_score: int
        Scenic score of the given tree position.
    """
    row_id, col_id = tree_position
    tree_height = trees[row_id, col_id]

    num_rows, num_columns = len(trees), len(trees[0])

    elements_to_left = trees[row_id, :col_id]
    elements_to_right = trees[row_id, col_id + 1 :]
    elements_below = (
        trees[row_id + 1 :, col_id] if (row_id + 1) < num_rows else np.asarray([])
    )
    elements_above = trees[:row_id, col_id] if row_id > 0 else np.asarray([])

    score = 1

    for direction, elements in (
        ("left", np.flip(elements_to_left)),
        ("right", elements_to_right),
        ("down", elements_below),
        ("up", np.flip(elements_above)),
    ):
        score *= count_visible_trees(tree_array=elements, tree_height=tree_height)

    return score


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> float:
    """Highest scenic score possible for any tree.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file to read tree elevation array from.

    Returns
    -------
    maximum_scenic_score: float
        Highest scenic score possible for any tree position.
    """
    trees = np.asarray(list(generate_trees(filepath=filepath)))

    best_scenic_score = float("-inf")

    num_rows, num_columns = len(trees), len(trees[0])

    for row_id in range(num_rows):
        for col_id in range(num_columns):
            tree_height = trees[row_id, col_id]

            score = scenic_score(tree_position=(row_id, col_id), trees=trees)

            best_scenic_score = max(best_scenic_score, score)

    return best_scenic_score


def main():
    print(part_1())
    print(part_2())


if __name__ == "__main__":
    main()
