from collections import defaultdict
from enum import Enum
from pathlib import Path
import re
import typing


class CubeColor(Enum):
    """Enumeration type for cube colors."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"

    @classmethod
    def from_string(cls, cube_color_str: str):
        str_enum_mapping = {enum_entry.value: enum_entry for enum_entry in cls}
        try:
            return str_enum_mapping[cube_color_str]
        except KeyError:
            raise


def generate_inputs(
    filepath: Path,
) -> typing.Iterable[typing.List[typing.Dict[CubeColor, int]]]:
    """Generate game inputs, one line at a time. Collapse game turns into flat list of mappings.

    Each inner dictionary represents one draw from the bag of a given (integer) number of cubes with a given cube color.

    Parameters:
    -----------
    filepath (pathlib.Path):
        Path to input file containing inputs on separate lines.

    Yields:
    -------
    game: typing.List[typing.Dict[CubeColor, int]]
        List representing the turns of the game (separated by ';' in the input file), each turn is composed of
        multiple draws from the bag, represented as dictionaries with color keys and (integer) cube number values.
    """
    cube_regex = (
        r"(?P<num_cubes>\d+) (?P<cube_color>blue|red|green)(?P<separator>,|;|$)"
    )
    with open(filepath) as f:
        for game_id, line in enumerate(f):
            drawn_cubes = [
                defaultdict(int)
            ]  # type: typing.List[typing.Dict[CubeColor, int]]
            for num_cubes_str, cube_color_str, separator in re.findall(
                pattern=cube_regex, string=line
            ):
                drawn_cubes[-1][CubeColor.from_string(cube_color_str)] += int(
                    num_cubes_str
                )

                if separator in ("", ";"):
                    drawn_cubes.append(defaultdict(int))
            yield drawn_cubes


def validate_turn(
    drawn_cubes_per_color: typing.Dict[CubeColor, int],
    available_cubes_per_color: typing.Dict[CubeColor, int],
) -> bool:
    """Validate if it is possible to draw `drawn_cubes_per_color` cubes from a bag containing `available_cubes_per_color`.

    Parameters:
    -----------
    drawn_cubes_per_color (typing.Dict[CubeColor, int]):
        Mapping of cube color to the number of cubes to take out of the bag.
    available_cubes_per_color (typing.Dict[CubeColor, int]):
        Mapping of cube color to the number of cubes available in the bag.

    Returns:
    -------
    is_draw_possible: bool
        Boolean determining if the extraction of `drawn_cubes_per_color` is possible.
    """
    for color, drawn_cubes in drawn_cubes_per_color.items():
        if drawn_cubes > available_cubes_per_color.get(color, 0):
            return False

    return True


def solution_part1(
    input_filepath: Path,
    available_cubes_per_color: typing.Dict[CubeColor, int] = {
        CubeColor.RED: 12,
        CubeColor.BLUE: 14,
        CubeColor.GREEN: 13,
    },
) -> int:
    """In game 1, three sets of cubes are revealed from the bag (and then put back again).
    The first set is 3 blue cubes and 4 red cubes; the second set is 1 red cube, 2 green cubes, and 6 blue cubes; the third set is only 2 green cubes.

    The Elf would first like to know which games would have been possible if the bag contained only 12 red cubes, 13 green cubes, and 14 blue cubes?
    Determine which games would have been possible if the bag had been loaded with only 12 red cubes, 13 green cubes, and 14 blue cubes.
    What is the sum of the IDs of those games?
    """
    valid_game_ids = set()
    for game_id, game in enumerate(generate_inputs(input_filepath), 1):
        is_valid_game = all(
            validate_turn(
                drawn_cubes_per_color=cubes_drawn_in_turn,
                available_cubes_per_color=available_cubes_per_color,
            )
            for cubes_drawn_in_turn in game
        )

        if is_valid_game:
            valid_game_ids.add(game_id)
    return sum(valid_game_ids)


def solution_part2(
    input_filepath: Path,
) -> int:
    """The power of a set of cubes is equal to the numbers of red, green, and blue cubes multiplied together.

    For each game, find the minimum set of cubes that must have been present.
    What is the sum of the power of these sets?
    """
    game_powers = []

    for game in generate_inputs(input_filepath):
        required_game_specs = defaultdict(int)  # type: typing.Dict[CubeColor, int]

        for turn in game:
            for color, num_cubes in turn.items():
                required_game_specs[color] = max(required_game_specs[color], num_cubes)

        game_powers.append(
            required_game_specs[CubeColor.RED]
            * required_game_specs[CubeColor.BLUE]
            * required_game_specs[CubeColor.GREEN]
        )

    return sum(game_power for game_power in game_powers)


def main():
    input_filepath = Path(__file__).parent.joinpath("data", "data.txt")
    print("PART 1:", solution_part1(input_filepath))
    print("PART 2:", solution_part2(input_filepath))


if __name__ == "__main__":
    main()
