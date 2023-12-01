from pathlib import Path
import typing


def generate_inputs(filepath: Path) -> typing.Iterable[str]:
    """Generate input lines from the given file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        path to file containing inputs, with digits both spelled out as well as represented as numbers on each line.

    Yields
    ------
    input_line: typing.list[int]
        The next input line from the file, without any preprocessing applied.
    """
    with open(filepath) as f:
        for line in f:
            yield line.strip()

def get_first_and_last_digit(
    string: str,
    digit_match_dict: typing.Dict[str, int] = {
        str(digit): digit for digit in range(1, 10)
    }
) -> typing.Tuple[int, int]:
    """Obtain first and last digit from the given string, matching digit names using a lookup dictionary.

    If a line contains only one single digit, this digit is both the first and last digit.

    Parameters
    ----------
    string : str
        String to match digits in.

    digit_match_dict: str, optional
        Dictionary used to identify digits. 
        Allows specifying that e.g., "one" should be mapped to digit `1`.

    Returns
    ------
    first_digit: int
        First digit encountered in the given string, using `digit_match_dict` to identify them.
    last_digit: int
        Last digit encountered in the given string, using `digit_match_dict` to identify them.
        The same as `first_digit` if there is only one digit in the given input string.
    """

    digits = []

    for i in range(len(string)):
        for digit_name, digit in digit_match_dict.items():
            if string[i: i + len(digit_name)] == digit_name:
                digits.append(digit)

    if len(digits) == 1:
        digit, = digits
        first_digit, last_digit = (digit, digit)
    else:
        first_digit, *_, last_digit = digits

    return first_digit, last_digit


def part1_solution():
    """Compute sum across lines, concatenating first and last digit of each line.
       Use only actual (numeric) digits to identify digits in each line.
    """
    calibration_values = []
    for line in generate_inputs(Path(__file__).parent.joinpath("data", "data.txt")):
        first_digit, last_digit = get_first_and_last_digit(line)
        calibration_values.append(int(f"{first_digit}{last_digit}"))
    return sum(calibration_values)

def part2_solution():
    """Compute sum across lines, concatenating first and last digit of each line.
       Use both numeric and verbose (e.g., "one" for digit "1") digit representations to identify digits in each line.
    """
    digit_match_dict = {
        **{
            digit_name: digit
            for digit, digit_name in enumerate(("one", "two", "three", "four", "five", "six", "seven", "eight", "nine"), 1)
        },
        **{
            str(digit): digit
            for digit in range(1, 10)
        }
    }

    calibration_values = []

    for line in generate_inputs(Path(__file__).parent.joinpath("data", "data.txt")):
        first_digit, last_digit = get_first_and_last_digit(line, digit_match_dict=digit_match_dict)
        calibration_values.append(int(f"{first_digit}{last_digit}"))
    return sum(calibration_values)


def main():
    print("PART 1:", part1_solution())
    print("PART 2:", part2_solution())

if __name__ == "__main__":
    main()
