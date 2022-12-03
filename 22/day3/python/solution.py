from pathlib import Path
from string import ascii_lowercase, ascii_uppercase
import typing


ALPHABET = ascii_lowercase + ascii_uppercase


def item_priority(item_char: str) -> int:
    assert (len(item_char) == 1) and (item_char in ALPHABET)
    return ALPHABET.index(item_char) + 1

def generate_rucksack_compartments(
    filepath:Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> typing.Iterable[typing.Tuple[str, str]]:
    with open(filepath, "r") as rucksack_file:
        for rucksack_contents in rucksack_file:
            num_items = len(rucksack_contents)
            first_compartment, second_compartment = (
                rucksack_contents[:num_items // 2],
                rucksack_contents[num_items // 2:],
            )
            yield first_compartment, second_compartment

def generate_elf_group_rucksacks(
    filepath:Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> typing.Iterable[typing.Tuple[str, str, str]]:

    with open(filepath, "r") as rucksack_file:
        elf_group_index, elf_group = 0, []
        for rucksack_contents in rucksack_file:
            elf_group.append(rucksack_contents.strip())

            elf_group_index += 1

            if ((elf_group_index % 3) == 0):
                yield tuple(elf_group)
                elf_group = []

        if elf_group:
            yield tuple(elf_group)


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> int:

    common_item_priority = 0

    for left_compartment, right_compartment in generate_rucksack_compartments(filepath=filepath):
        common_items = set(left_compartment).intersection(right_compartment)
        common_item_priority += sum(item_priority(item) for item in common_items)

    return common_item_priority

def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> int:

    badge_item_priority_sum = 0
    for elf_group in generate_elf_group_rucksacks(filepath=filepath):
        try:
            badge_item, = set.intersection(*map(set, elf_group))
        except ValueError:
            raise ValueError(
                f"Multiple shared items in elf group: '{elf_group}'. "
                f"Shared items were: {set.intersection(*map(set, elf_group))}"
            )

        badge_item_priority_sum += item_priority(badge_item)
    return badge_item_priority_sum

print(part_1())
print(part_2())




