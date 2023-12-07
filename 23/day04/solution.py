from pathlib import Path
import re
import typing


def generate_inputs(
    filepath: Path,
) -> typing.Iterable[typing.Dict[str, typing.Union[int, typing.List[int]]]]:
    """Generate score card details, one card at a time.

    Parameters:
    -----------
    filepath (pathlib.Path):
        Input filepath to read data from.

    Yields:
    -------
    card_details (typing.Dict[str, typing.Union[int, typing.List[int]]]):
        Scorecard detail mappings, with string keys:
        * card_id (str):
            String ID of the scorecard.
        * winning_numbers (typing.List[int]):
            Numbers that win points for the given scorecard.
        * card_numbers (typing.List[int]):
            Numbers we have on the card, to be compared against the corresponding `winning_numbers`.
    """
    regex_pattern = r"Card (?P<card_id>[0-9 ]+): "
    numbers_pattern = r"(?P<numbers>[0-9]+)"

    with open(filepath, "r") as f:
        for line in f:
            match = re.search(pattern=regex_pattern, string=line.strip())

            if match is None:
                raise ValueError(f"Invalid input line: {line.strip()}")

            _, line = line.split(":")
            left, right = line.split("|")
            card_id = int(match.group("card_id").strip())
            winning_numbers = [
                int(number)
                for number in re.findall(pattern=numbers_pattern, string=left.strip())
                if number.strip()
            ]
            card_numbers = [
                int(number)
                for number in re.findall(pattern=numbers_pattern, string=right.strip())
                if number.strip()
            ]

            yield {
                "card_id": card_id,
                "winning_numbers": winning_numbers,
                "card_numbers": card_numbers,
            }


def score_scratchcard(
    card_numbers: typing.Iterable[int],
    winning_numbers: typing.Iterable[int],
):
    """Score a given scratchcard for points based on matches between card numbers and winning numbers.

    Parameters:
    -----------
    card_numbers (typing.Iterable[int]):
        Our numbers on a given scorecard.
    winning_numbers (typing.Iterable[int]):
        Numbers earning points for the given scorecard.

    Returns:
    --------
    card_score (int):
        `0` if and only if no card numbers are contained in the winning numbers.
        Otherwise `2 ** (num_matches - 1)`.
    """
    num_matches = len(set(card_numbers).intersection(winning_numbers))

    if not num_matches:
        return 0

    return 2 ** (num_matches - 1)


def part1(filepath: Path) -> int:
    """Total scored points across all scratchcards."""
    return sum(
        score_scratchcard(
            card_numbers=card_details["card_numbers"],
            winning_numbers=card_details["winning_numbers"],
        )
        for card_details in generate_inputs(filepath=filepath)
    )


def part2(filepath: Path):
    """Total number of cards after copying scratchcards based on the number of matched numbers."""
    scratchcards = [card for card in generate_inputs(filepath=filepath)]
    num_scratchcards = len(scratchcards)

    num_matches_per_scratchcard = [
        len(
            set(card_details["card_numbers"]).intersection(
                card_details["winning_numbers"]
            )
        )
        for card_details in scratchcards
    ]

    # Start with a single scratchcards
    num_cards = [1] * num_scratchcards

    for scratch_card_index, num_matches in enumerate(num_matches_per_scratchcard):
        for match_index in range(num_matches):
            num_cards[scratch_card_index + match_index + 1] += num_cards[
                scratch_card_index
            ]

    return sum(num_cards)


def main():
    filepath = Path(__file__).parent.joinpath("data", "data.txt")
    print("PART 1:", part1(filepath))
    print("PART 2:", part2(filepath))


if __name__ == "__main__":
    main()
