from pathlib import Path
import re
import typing

def generate_assignment_pairs(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> typing.Iterable[typing.Tuple[str, str]]:

    with open(filepath) as assignments_file:
        for line in assignments_file:
            left_assignment, right_assignment = line.split(",")
            yield left_assignment, right_assignment

def assignment_to_range_set(
    assignment: str,
    regex_pattern: str = r"(?P<assignment_start>\d+)-(?P<assignment_end>\d+)"
) -> typing.Set[int]:
    match = re.match(string=assignment, pattern=regex_pattern)

    if not match:
        raise ValueError()

    assignment_start = int(match.group("assignment_start"))
    assignment_end = int(match.group("assignment_end"))

    return set(range(assignment_start, assignment_end + 1))

def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> int:
    num_contained_pairs = 0
    for left_assignment, right_assignment in generate_assignment_pairs(filepath=filepath):
        left_range, right_range = (
            assignment_to_range_set(left_assignment),
            assignment_to_range_set(right_assignment)
        )

        if left_range.issubset(right_range) or right_range.issubset(left_range):
            num_contained_pairs += 1

    return num_contained_pairs

def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> int:
    num_overlapping_pairs = 0
    for left_assignment, right_assignment in generate_assignment_pairs(filepath=filepath):
        left_range, right_range = (
            assignment_to_range_set(left_assignment),
            assignment_to_range_set(right_assignment)
        )

        if left_range.intersection(right_range) or right_range.intersection(left_range):
            num_overlapping_pairs += 1

    return num_overlapping_pairs

def main():
    print(part_1())
    print(part_2())

if __name__ == "__main__":
    main()
