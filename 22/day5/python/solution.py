from collections import deque
from pathlib import Path
import re
import typing


def parse_crate_configuration_and_commands(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
):
    """Parse initial crate configuration and instructions for moving crates.

    Parameters
    ----------
    filepath: Path, optional
        Input filepath to read data from.

    Returns
    -------
    crate_configurations: typing.List[collections.deque]
        Initial configuration of all crates. Each crate is represented as
        a `collections.deque` object to allow for fast insertion and removal
        of the first element.
    crate_move_instructions: typing.List[typing.Dict[str, int]]
        Parameters to govern moving objects between a source and target crate.
        Contains keys `num_crates`, `source`, `target` whereby `source` and
        `target` are zero-indexed crane-id's between which to move `num_crates` crates.
    """
    crate_line_regex = r"( ?   ?| ?[A-Z] ?)"  # Regex to parse crate contents

    # Regex to parse instructions for moving crates.
    command_regex = r"move (?P<num_crates>\d+) from (?P<source>\d+) to (?P<target>\d+)"

    with open(filepath, "r") as crate_file:

        # Pre-fetch one line to build the crate configuration for later usage.
        line = next(crate_file)
        crate_matches = re.findall(string=line, pattern=crate_line_regex)
        crate_configuration = [
            deque(crate.strip()) if crate.strip() else deque()
            for crate in crate_matches
        ]

        while True:
            line = next(crate_file)
            crate_matches = re.findall(string=line, pattern=crate_line_regex)

            if not crate_matches:
                # Ran out of crate lines to match, start parsing commands
                break

            for i, crate_match in enumerate(crate_matches):
                if crate_match.strip():
                    crate_configuration[i].appendleft(crate_match)

        # Parse instructions for moving crates, as dictionaries
        commands = []
        for command_line in crate_file:
            match = re.search(string=command_line.strip(), pattern=command_regex)
            command = {
                command_parameter: int(parameter_value)
                for command_parameter, parameter_value in match.groupdict().items()
            }
            # NOTE: Convert to zero-index
            command["source"] -= 1
            command["target"] -= 1
            commands.append(command)

        return crate_configuration, commands


def part_1(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> str:
    """Topmost crates after moving crates one at a time, reversing order of moved crates.

    Parameters
    ----------
    filepath: Path, optional
        Input filepath to read data from.

    Returns
    -------
    topmost_crate_ids: str
        Concatenated ID's of topmost crates after executing all instructions to
        move crates.
    """
    crate_configuration, commands = parse_crate_configuration_and_commands(
        filepath=filepath
    )

    topmost_crates = []
    for command in commands:
        for num_crates in range(command["num_crates"]):
            crate_configuration[command["target"]].append(
                crate_configuration[command["source"]].pop()
            )

    topmost_crates = [configuration[-1] for configuration in crate_configuration]
    return "".join(topmost_crates)


def part_2(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> str:
    """Topmost crates after moving crates many at a time, maintaining order of moved crates.

    Parameters
    ----------
    filepath: Path, optional
        Input filepath to read data from.

    Returns
    -------
    topmost_crate_ids: str
        Concatenated ID's of topmost crates after executing all instructions to
        move crates.
    """
    crate_configuration, commands = parse_crate_configuration_and_commands(
        filepath=filepath
    )

    for command in commands:
        crates_to_move = deque()

        for _ in range(command["num_crates"]):
            crates_to_move.appendleft(crate_configuration[command["source"]].pop())

        crate_configuration[command["target"]].extend(crates_to_move)

    topmost_crates = [configuration[-1] for configuration in crate_configuration]
    return "".join(topmost_crates)


def main():
    print("PART 1:",  part_1())
    print("PART 2:",  part_2())


if __name__ == "__main__":
    main()
