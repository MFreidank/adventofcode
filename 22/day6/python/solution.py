from pathlib import Path


def find_non_repeating_characters(
    datastream: str,
    num_non_repeating_characters: int,
) -> int:
    """Return number of characters in `datastream` that need to be processed before a
       sequence of `num_non_repeating_characters` characters that are all different
       is reached.

    Parameters
    ----------
    datastream : str
        Stream of characters, expected to contain a sequence of
        `num_non_repeating_characters` characters that are all different.
    num_non_repeating_characters : int
        Length of subsequence such that all characters in the subsequence are different.

    Returns
    -------
    num_characters_to_process: int
        Number of characters to process before subsequence is found.
    """
    for slice_start_index in range(0, len(datastream), 1):
        slice_end_index = slice_start_index + num_non_repeating_characters
        chars = datastream[slice_start_index:slice_end_index]

        if len(chars) == len(set(chars)):
            return slice_end_index

    raise ValueError(
        f"No sequence of non-repeating characters of length '{num_non_repeating_characters}' "
        f"contained in datastream: '{datastream}'."
    )


def part_1(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> int:
    with open(filepath, "r") as datastream_file:
        datastream = datastream_file.read().rstrip()

    return find_non_repeating_characters(
        datastream,
        num_non_repeating_characters=4,
    )


def part_2(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")):
    with open(filepath, "r") as datastream_file:
        datastream = datastream_file.read().rstrip()

    return find_non_repeating_characters(
        datastream,
        num_non_repeating_characters=14,
    )


def main():
    print("PART 1:", part_1())
    print("PART 2:", part_2())


if __name__ == "__main__":
    main()
