import heapq
from pathlib import Path
import typing


def generate_elf_calories_from_file(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> typing.Iterable[typing.List[int]]:
    """Generate calories carried by each individual elve from a plain text input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path containing numeric inputs, one number per line. Separated into elfs by emptylines.

    Yields
    ------
    single_elf_calories: typing.list[int]
        The next number from the file, converted to an integer.
    """
    with open(filepath, "r") as numbers_file:
        single_elf_calories: typing.List[int] = []

        for line in numbers_file:
            if not line.strip():
                yield single_elf_calories
                single_elf_calories = []
            else:
                single_calorie_entry = int(line.strip())
                single_elf_calories.append(single_calorie_entry)

        yield single_elf_calories


def carried_calories_per_elf(elf_calories) -> typing.Iterable[int]:
    """Total calories carried for each elf in the file.

    Parameters
    ----------
    elf_calories : typing.Iterable[typing.List[int]]
        Iterator over lists, each inner list (one elf) element represents calories of
        one item of the corresponding elf.

    Returns
    -------
    calories_per_elf: typing.Iterable[int]
        Iterator over total calories carried by each elf.
    """
    return (
        sum(single_elf_calories) for single_elf_calories in generate_elf_calories_from_file()
    )


def part_1_solution(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> int:
    """Maximum amount of calories carried by an elf.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path containing numeric inputs, one number per line. Separated into elfs by emptylines.

    Returns
    -------
    max_calories_across_elves: typing.Iterable[int]
        Highest calories carried by any single elf.
    """
    return max(
        carried_calories_per_elf(generate_elf_calories_from_file(filepath=filepath))
    )


def part_2_solution(
    filepath: Path = Path(__file__).parent.joinpath("inputs.txt"),
    num_highest_calorie_elfs_to_consider: int = 3,
) -> int:
    """Sum of calories carried by the elves carrying the most calories.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path containing numeric inputs, one number per line. Separated into elfs by emptylines.
    num_highest_calorie_elfs_to_consider: int, optional
        Number of elves carrying the most calories to consider.

    Returns
    -------
    calories_carried: int
        Sum of calories carried by elves carrying the most calories.
    """

    highest_calories_carried = heapq.nlargest(
        n=num_highest_calorie_elfs_to_consider,
        iterable=carried_calories_per_elf(
            generate_elf_calories_from_file(filepath=filepath)
        )
    )

    return sum(highest_calories_carried)


def main():
    print("PART 1:", part_1_solution())
    print("PART 2:", part_2_solution())


if __name__ == "__main__":
    main()
