from pathlib import Path
import typing

WIN_SCORE_POINTS = 6
DRAW_SCORE_POINTS = 3


class Move(object):
    def __init__(self, name: str):
        assert name in ("Rock", "Paper", "Scissor")
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def score(self, opponent_move) -> int:
        assert isinstance(opponent_move, Move)

        move_score = ("Rock", "Paper", "Scissor").index(self.name) + 1

        if self > opponent_move:
            move_score += WIN_SCORE_POINTS
        elif self == opponent_move:
            move_score += DRAW_SCORE_POINTS

        return move_score

    def __eq__(self, other):
        assert isinstance(other, Move)
        return self.name == other.name

    def __gt__(self, other):
        match (self.name, other.name):
            case ("Rock", "Scissor"):
                return True
            case ("Paper", "Rock"):
                return True
            case ("Scissor", "Paper"):
                return True
            case _:
                return False


def generate_guide_from_file(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[typing.Tuple[str, str]]:
    with open(filepath, "r") as f:
        for line in f:
            opponent_choice, my_choice = line.strip().split(" ")
            yield opponent_choice, my_choice


def part_1(filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")) -> int:
    choice_to_move = {
        "A": Move(name="Rock"),
        "B": Move(name="Paper"),
        "C": Move(name="Scissor"),
        "X": Move(name="Rock"),
        "Y": Move(name="Paper"),
        "Z": Move(name="Scissor"),
    }

    game_score = 0

    for opponent_choice, my_choice in generate_guide_from_file(filepath=filepath):
        opponent_move, my_move = choice_to_move[opponent_choice], choice_to_move[my_choice]

        game_score += my_move.score(opponent_move=opponent_move)

    return game_score


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt")
) -> int:
    desired_result_mapping = {"X": "loss", "Y": "draw", "Z": "win"}
    choice_to_move = {
        "A": Move(name="Rock"), "B": Move(name="Paper"), "C": Move(name="Scissor"),
    }
    moves = choice_to_move.values()

    move_to_choose = {
        **{
            ("draw", opponent_move): opponent_move
            for opponent_move in choice_to_move.values()
        },
        **{
            ("win", opponent_move): next(
                counter_move for counter_move in moves if counter_move > opponent_move
            )
            for opponent_move in moves
        },
        **{
            ("loss", opponent_move): next(
                counter_move for counter_move in moves if counter_move < opponent_move
            )
            for opponent_move in moves
        },
    }

    game_score = 0

    for opponent_choice, encoded_desired_result in generate_guide_from_file(filepath=filepath):
        desired_result = desired_result_mapping[encoded_desired_result]
        opponent_move = choice_to_move[opponent_choice]

        my_move = move_to_choose[(desired_result, opponent_move)]

        game_score += my_move.score(opponent_move)

    return game_score


print(part_1())
print(part_2())
