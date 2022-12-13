import ast
import functools
from pathlib import Path
import typing

def generate_pairs(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")):
    """Generate input pairs (as python lists) from the given input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to advent of code input file.

    Yields
    ------
    typing.Tuple[typing.List[typing.Any], typing.List[typing.Any]]:
        Pairs of nested inputs, without any pre-processing except for conversion to list.
    """
    with open(filepath, "r") as inputs_file:
        line_iterator = iter(inputs_file)

        while True:
            left_items = ast.literal_eval(next(line_iterator).strip())
            right_items = ast.literal_eval(next(line_iterator).strip())

            yield left_items, right_items

            # Skip empty lines separating input pairs
            try:
                _ = next(line_iterator)
            except StopIteration:
                # NOTE: End of file, simply return
                return

def pairwise_comparison(
    left_item: typing.Union[int, typing.List[typing.Any]],
    right_item: typing.Union[int, typing.List[typing.Any]]
) -> int:
    """Compare the given pair of items recursively to determine if they are equal
       or the left item is smaller or the right item is smaller.
       Implemented as a comparison function.

    Parameters
    ----------
    left_item : typing.Union[int, typing.List[typing.Any]]
        Left element to compare.
    right_item : typing.Union[int, typing.List[typing.Any]]
        Right element to compare.

    Returns
    -------
    cmp_result: int
        One of:
        * 0 if and only if left item and right item compare equally
        * 1 if and only if left item < right item in the comparison
        * -1 if and only if left item > right item in the comparison
    """
    if right_item == [] and left_item == []:
        return 1
    elif right_item == []:
        return -1
    elif left_item == []:
        return 1

    # If both items are integers, simply compare them as integers.
    if isinstance(left_item, int) and isinstance(right_item, int):
        if left_item < right_item:
            return 1
        elif left_item > right_item:
            return -1
        else:
            return 0
    # If only one item is an integer, wrap it in a list and compare recursively
    elif isinstance(left_item, int):
        return pairwise_comparison(
            left_item=[left_item],
            right_item=right_item,
        )
    elif isinstance(right_item, int):
        return pairwise_comparison(
            left_item=left_item,
            right_item=[right_item],
        )
    else:
        # If both items are lists, compare their respective first elements
        # and recurse into the list tails if needed.
        (left_element, *left_item), (right_element, *right_item) = left_item, right_item

        # NOTE: Special case: At the end of comparison of an equal length sublist,
        # both elements can be empty lists but we still need to recurse into the
        # tails. First check if the tails are also empty lists and return if yes.
        if left_element == [] and right_element == []:
            if left_item == [] and right_item == []:
                # All empty, can be treated as "left list ran out of items"
                return 1
            else:
                # Tail items may remain, let's compare them.
                return pairwise_comparison(left_item, right_item)

        # Compare first elements
        element_comparison = pairwise_comparison(left_item=left_element, right_item=right_element)

        # If comparison is conclusive (left smaller == 1 or left larger == -1)
        # return its result
        if element_comparison != 0:
            return element_comparison

        # ...otherwise recurse into the tails
        return pairwise_comparison(
            left_item,
            right_item,
        )

def is_pair_sorted(
    left_item: typing.Union[int, typing.List[typing.Any]],
    right_item: typing.Union[int, typing.List[typing.Any]],
    comparison_function: typing.Callable = pairwise_comparison):
    """Shorthand to check if a given pair is sorted according to the comparison function.

    Parameters
    ----------
    left_item : typing.Union[int, typing.List[typing.Any]]
        Left element to compare.
    right_item : typing.Union[int, typing.List[typing.Any]]
        Right element to compare.
    pairwise_comparison: typing.Callable
        Comparison function that maps two inputs to their comparison value (0, 1 or -1).

    Returns
    -------
    is_left_item_smaller_equal: bool
        True if and only if the left item compares as smaller or equal to the right item.
    """
    return comparison_function(left_item, right_item) in (0, 1)


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
):
    """Sum of indices (starting at 1) of sorted pairs in the given input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to advent of code input file.

    Returns
    -------
    index_sum: int
        Sum of indices (starting at 1) of sorted pairs in the given input file.
    """
    return sum(
        index for index, pair in enumerate(generate_pairs(filepath=filepath), 1)
        if is_pair_sorted(*pair)
    )

def part_2(
    filepath: Path =Path(__file__).parent.parent.joinpath("inputs.txt"),
    divider_packets: typing.List[typing.List[typing.Any]] = [[[2]], [[6]]],
):
    """Result of multiplying indices of divider packets in sorted list of inputs
       when divider packets are included.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to advent of code input file.
    divider_packets : typing.List[typing.List[int], typing.List[int]]
        Divider packets to include and retrieve.

    Returns
    -------
    divider_packet_index_multiplication: int
        Result of multiplying indices of divider packets in sorted list of inputs
        when divider packets are included.
    """
    items = list(divider_packets)

    for left, right in generate_pairs(filepath=filepath):
        items.extend([left, right])

    sorted_items = sorted(items, key=functools.cmp_to_key(pairwise_comparison), reverse=True)

    return (sorted_items.index(divider_packets[0]) + 1) * (sorted_items.index(divider_packets[1]) + 1)


def main():
    print(part_1())
    print(part_2())

if __name__ == "__main__":
    main()
