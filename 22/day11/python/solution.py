from collections import deque
from math import lcm
from operator import add, mul
from pathlib import Path
import re
import typing


class Monkey:
    """Class representing a monkey from the puzzle."""

    def __init__(
        self,
        items,
        op,
        op_value,
        divisor,
        throw_to_index_if_true,
        throw_to_index_if_false,
        num_inspections: int = 0,
    ) -> None:
        """Initialize monkey attributes.

        Parameters
        ----------
        items: collections.deque
            Numbers representing items currently held by this monkey.
        op: typing.Callable
            Operation to update worry level with when this monkey inspects an item.
        op_value: int
            Value to feed to the monkey operation.
        divisor: int
            Divisor of the test for this monkey.
        throw_to_index_if_true: int
            Index of monkey to throw item to if division test is true.
        throw_to_index_if_false: int
            Index of monkey to throw item to if division test is false.
        num_inspections: int, optional
            Number of inspections done by this monkey. Default: `0`.
        """
        self.items = items
        self.op = op
        self.op_value = op_value
        self.divisor = divisor
        self.throw_to_index_if_true = throw_to_index_if_true
        self.throw_to_index_if_false = throw_to_index_if_false
        self.num_inspections = num_inspections

    def inspect(self) -> int:
        """Inspect an item with this monkey, returning worry level associated
           with his operation.

        Returns
        -------
        worry_level: int
            Worry level resulting from monkey inspecting his leftmost item.
        """
        item = self.items.popleft()

        if self.op_value is None:
            return self.op(item, item)

        return self.op(item, self.op_value)


def run_monkey_simulation(
    monkeys: typing.List[Monkey],
    num_rounds: int,
    is_part_2: bool = False,
) -> int:
    """Run a given number of simulation rounds with the monkeys.

    Parameters
    ----------
    monkeys : typing.List[Monkey]

    num_rounds : int

    is_part_2 : bool, optional
        Boolean flag that changes simulation behaviour for part 2.
        Trick is to use modulo calculation with the least common multiple across
        operation divisors instead of division by 3.

    Returns
    -------
    inspection_num_multiplication_result: int
        Result of multiplying the number of inspections performed by
        the two monkeys that have performed the most inspections.
    """
    pass
    if is_part_2:
        modulus = lcm(*(monkey.divisor for monkey in monkeys))

    for _ in range(num_rounds):
        for monkey in monkeys:
            monkey.num_inspections += len(monkey.items)

            while monkey.items:
                if is_part_2:
                    item = monkey.inspect() % modulus
                else:
                    item = monkey.inspect() // 3

                if (item % monkey.divisor) == 0:
                    monkeys[monkey.throw_to_index_if_true].items.append(item)
                else:
                    monkeys[monkey.throw_to_index_if_false].items.append(item)

    highest_num_inspections, second_highest_num_inspections, *_ = sorted(
        (monkey.num_inspections for monkey in monkeys), reverse=True
    )
    return highest_num_inspections * second_highest_num_inspections


def generate_monkeys_from_file(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[Monkey]:
    """Generate monkey objects from a raw advent of code input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file containing monkey definitions.

    Yields
    ------
    monkeys: typing.Iterable[Monkey]
        Monkey objects populated with relevant attributes.
    """
    numbers_pattern = re.compile(r"\d+")

    with open(filepath, "r") as inputs_file:
        monkey_blocks = inputs_file.read().split("\n\n")

    for monkey_block in monkey_blocks:
        lines = monkey_block.splitlines()

        (
            _,
            items_line,
            operation_line,
            divisor_line,
            throw_to_true_line,
            throw_to_false_line,
        ) = lines

        matches = re.search(
            pattern=numbers_pattern,
            string=operation_line,
        )

        monkey = Monkey(
            items=deque(map(int, numbers_pattern.findall(items_line))),
            op=add if "+" in operation_line else mul,
            op_value=int(matches.group()) if matches else None,
            divisor=int(numbers_pattern.search(divisor_line).group()),
            throw_to_index_if_true=int(
                numbers_pattern.search(throw_to_true_line).group()
            ),
            throw_to_index_if_false=int(
                numbers_pattern.search(throw_to_false_line).group()
            ),
        )
        yield monkey


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    num_rounds: int = 20,
):
    """Level of monkey business after `num_rounds`, dividing worry level
       by 3 after monkey inspections.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file containing monkey definitions.
    num_rounds : int, optional
        Number of rounds to run the simulation for. Default: `20`.

    Returns
    -------
    level_of_monkey_business: int
        Level of monkey business (multiplication result of the number of inspections
        of the two monkeys that performed the most inspections).
    """
    monkeys = tuple(generate_monkeys_from_file(filepath=filepath))

    return run_monkey_simulation(monkeys, num_rounds=num_rounds, is_part_2=False)


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    num_rounds: int = 10_000,
):
    """Level of monkey business after `num_rounds`, *without* dividing worry level
       by 3 after monkey inspections.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file containing monkey definitions.
    num_rounds : int, optional
        Number of rounds to run the simulation for. Default: `10_000`

    Returns
    -------
    level_of_monkey_business: int
        Level of monkey business (multiplication result of the number of inspections
        of the two monkeys that performed the most inspections).
    """
    monkeys = tuple(generate_monkeys_from_file(filepath=filepath))

    return run_monkey_simulation(monkeys, num_rounds=num_rounds, is_part_2=True)


def main():
    print("Part 1:", part_1())
    print("Part 2:", part_2())


if __name__ == "__main__":
    main()
