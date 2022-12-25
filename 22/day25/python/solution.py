from collections import deque
from pathlib import Path
import typing

# Maps snafu chars to decimal representation
SNAFU_TO_DECIMAL_MAP = {
    **{i: int(i) for i in ("0", "1", "2")},
    "-": -1,
    "=": -2,
}

# Maps decimal integers to their SNAFU representation
DECIMAL_TO_SNAFU_MAP = {n: snafu_char for snafu_char, n in SNAFU_TO_DECIMAL_MAP.items()}


def parse_inputs(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[str]:
    """Read SNAFU numbers from an input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to the input file.

    Yields
    ------
    line: str
        Single SNAFU number from the file.
    """
    with open(filepath, "r") as f:
        for line in f:
            yield line.strip()


def snafu_to_decimal(snafu_number: str, base_multiplier: int = 5) -> int:
    """Convert SNAFU number (given as string digits) to decimal integer representation.

    Parameters
    ----------
    snafu_number : str
        SNAFU number (given as string digits).
    base_multiplier : int, optional
        Base multiplier per digit to assume. Default: `5`.

    Returns
    -------
    decimal_number: int
        Integer decimal number corresponding to the input SNAFU number.
    """
    return sum(
        SNAFU_TO_DECIMAL_MAP[snafu_digit] * (5**digit_index)
        for digit_index, snafu_digit in enumerate(reversed(snafu_number))
    )


def decimal_to_base(decimal_number: int, base: int = 5) -> typing.List[int]:
    """Represent the given decimal number in the given base.

    Parameters
    ----------
    decimal_number : int
        Decimal number to convert to a new base.
    base : int, optional
        Base to convert to. Default: `5`.

    Returns
    -------
    base_digits: str
        Digits represented as string, of the input number converted to the given base.
    """
    digits = deque()
    while decimal_number:
        digits.appendleft(str(decimal_number % base))
        decimal_number //= base

    return "".join(digits)


def decimal_to_snafu(decimal_number: int, base: int = 5) -> str:
    """Convert a given decimal number to SNAFU, assuming a given SNAFU base.

    Parameters
    ----------
    decimal_number : int
        Decimal number to convert to SNAFU.

    base : int, optional
        Base to use as intermediate for converstion. Default: `5`.

    Returns
    -------
    snafu_number: str
        SNAFU number after conversion.
    """
    base_five_number = decimal_to_base(decimal_number, base=base)

    snafu_digits = []
    remainder = 0

    # NOTE: Process digits of base 5 number in reverse, truncating to
    # SNAFU using simple remainder logic.
    for digit in map(int, reversed(base_five_number)):
        digit += remainder
        remainder = 0

        if digit in (0, 1, 2):
            snafu_digits.append(DECIMAL_TO_SNAFU_MAP[digit])
        # If after adding remainder the digit is too large to be represented
        # in SNAFU (i.e., in `(3, 4, 5)`) truncate and move a remainder forward.
        elif digit in (3, 4, 5):
            current_digit, remainder = (digit - base), 1
            snafu_digits.append(DECIMAL_TO_SNAFU_MAP[current_digit])
        else:
            raise ValueError(f"Invalid digit encountered: '{digit}'.")

    if remainder:  # If we still have a remainder after the loop, append a "1"
        snafu_digits.append("1")

    # Re-reverse digits to get the actual number.
    return "".join(reversed(snafu_digits))


def part_1(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> str:
    """Compute SNAFU representation of sum of SNAFU numbers in the input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to the input file.

    Returns
    -------
    snafu_result: str
        Final SNAFU number that is the sum of all input SNAFU numbers in the file..
    """
    decimal_sum = sum(
        snafu_to_decimal(snafu_number)
        for snafu_number in parse_inputs(filepath=filepath)
    )

    return decimal_to_snafu(decimal_sum)


def main():
    print("Part 1:", part_1())
    print("Part 2: There is no part 2 :(")


if __name__ == "__main__":
    main()
