from pathlib import Path
import typing

import numpy as np


def generate_instructions(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")):
    """Generate instructions as dictionaries.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to advent of code input file.

    Yields
    -------
    instruction_dict: typing.Dict[str, typing.Union[str, int]]
        Instructions consist of the name of the instruction, the number of cycles
        required to process them and the increase of the register value that results
        after processing is finished.
    """
    with open(filepath, "r") as f:
        for line_ in f:
            line = line_.strip()

            if line == "noop":
                yield {
                    "name": "noop",
                    "num_cycles": 1,
                    "register_increase": 0,
                }
            else:
                instruction_name, register_increase = line.split()
                assert instruction_name == "addx"
                yield {
                    "name": instruction_name,
                    "num_cycles": 2,
                    "register_increase": int(register_increase),
                }

def report_cycle_values(
    instructions: typing.Iterable[typing.Dict[str, typing.Union[str, int]]],
    first_cycle_to_report: int = 20,
    cycle_to_report_increment: int = 40,
) -> typing.Iterable[typing.Tuple[int, int]]:
    """Report cycle values at given checkpoints.

    Parameters
    ----------
    instructions : typing.Iterable[typing.Dict[str, typing.Union[str, int]]]
        Instruction generator. Instructions each consist of the name of the instruction, the number of cycles
        required to process them and the increase of the register value that results
        after processing is finished.
    first_cycle_to_report : int, optional
        First cycle index whose value should be yielded. Default: `20`.
    cycle_to_report_increment : int, optional
        Increment to report values at, after the first cycle index. Default: `40`.

    Yields
    ------
    cycle_index: int
        Index of reported cycle iteration.
    cycle_value: int
        Register value of register X at the given reported cycle iteration.
    """
    num_cycles_processed, register_value = 0, 1

    next_cycle_to_report = int(first_cycle_to_report)

    instruction_iterator = iter(instructions)
    while True:
        try:
            instruction = next(instruction_iterator)
        except StopIteration:
            break

        for instruction_cycle_index in range(1, instruction["num_cycles"] + 1):
            if (num_cycles_processed + instruction_cycle_index) == next_cycle_to_report:
                yield next_cycle_to_report, register_value
                next_cycle_to_report += cycle_to_report_increment

        register_value += instruction["register_increase"]
        num_cycles_processed += instruction["num_cycles"]


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> int:
    """Sum of signal strengths at reported cycle indices.

       Signal strength at a cycle index is the result of multiplying the cycle
       index with the corresponding register value for that cycle.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to advent of code input file.

    Returns
    -------
    sum_of_signal_strengths: int
        Sum of signal strengths at reported cycle indices.
    """
    signal_strength = 0

    instructions = generate_instructions(filepath=filepath)

    for cycle_index, register_value in report_cycle_values(instructions):
        signal_strength += cycle_index * register_value

    return signal_strength


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> str:
    """CRT image after drawing all characters with a sprite controlled by register X.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to advent of code input file.

    Returns
    -------
    crt_image_as_str: str
        Final CRT image.
    """
    instructions = generate_instructions(filepath=filepath)

    num_cycles_processed = 0

    sprite_positions = np.asarray([0, 1, 2])
    crt_rows, current_crt_row = [], []

    instruction_iterator = iter(instructions)

    while True:
        try:
            instruction = next(instruction_iterator)
        except StopIteration:
            break

        for instruction_cycle_index in range(1, instruction["num_cycles"] + 1):
            crt_char = "#" if (len(current_crt_row) in sprite_positions) else "."
            current_crt_row.append(crt_char)

            if ((num_cycles_processed + instruction_cycle_index) % 40) == 0:
                crt_rows.append("".join(current_crt_row))
                current_crt_row = []

        sprite_positions = sprite_positions + instruction["register_increase"]
        num_cycles_processed += instruction["num_cycles"]

    return "\n".join(crt_rows)

def main():
    print("Part 1:", part_1())
    print("Part 2:")
    print(part_2())

if __name__ == "__main__":
    main()

