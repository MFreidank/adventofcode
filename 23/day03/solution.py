from collections import defaultdict
from itertools import product
from pathlib import Path
import typing


def generate_inputs(filepath: Path) -> typing.Iterable[str]:
    with open(filepath) as f:
        lines = f.readlines()

        for line in lines:
            yield line.strip()


def get_adjacent_indices(
    index: typing.Tuple[int, int],
    dimensions: typing.Tuple[int, int],
) -> typing.List[typing.Tuple[int, int]]:
    row_index, column_index = index

    num_rows, num_columns = dimensions

    adjacent_indices = []

    for dx in range(-1, 2):
        for dy in range(-1, 2):
            range_x = range(0, num_rows)
            range_y = range(0, num_columns)

            (new_x, new_y) = (row_index + dx, column_index + dy)  # adjacent cell

            if (new_x in range_x) and (new_y in range_y) and (dx, dy) != (0, 0):
                adjacent_indices.append((new_x, new_y))

    return adjacent_indices


def locate_numbers(grid):
    numbers, number_positions = [], []
    current_number, current_number_position = [], []
    for row_index, row in enumerate(grid):
        if current_number:
            numbers.append(int("".join(current_number)))
            # NOTE: Adjacency is determined only with respect to the first and last character of a number.
            # Retain only these positions for each number.
            min_column, max_column = (
                min(column_index for _, column_index in current_number_position),
                max(column_index for _, column_index in current_number_position),
            )
            number_row = current_number_position[0][0]
            number_positions.append(
                [(number_row, min_column), (number_row, max_column)]
            )
            current_number, current_number_position = [], []
        for column_index, character in enumerate(row):
            if character.isdigit():
                current_number.append(character)
                current_number_position.append((row_index, column_index))
            else:
                if current_number:
                    numbers.append(int("".join(current_number)))
                    # NOTE: Adjacency is determined only with respect to the first and last character of a number.
                    # Retain only these positions for each number.
                    min_column, max_column = (
                        min(
                            column_index for _, column_index in current_number_position
                        ),
                        max(
                            column_index for _, column_index in current_number_position
                        ),
                    )
                    number_row = current_number_position[0][0]
                    number_positions.append(
                        [(number_row, min_column), (number_row, max_column)]
                    )
                    current_number, current_number_position = [], []

    return numbers, number_positions

def generate_symbol_positions(
    grid: typing.List[str],
    is_symbol_function=lambda character: character == "$",
):
    for row_index, row in enumerate(grid):
        for column_index, character in enumerate(row):
            if is_symbol_function(character): 
                yield (row_index, column_index)



def is_adjacent_to_symbol_in_grid(
    grid: typing.List[str],
    number_position: typing.List[typing.Tuple[int, int]],
    is_symbol_function=lambda character: (
        (character != ".") and (not character.isdigit())
    ),
) -> bool:
    grid_dimensions = len(grid), len(grid[0])

    adjacency_squares = set.union(
        *(
            set(get_adjacent_indices(index=number_index, dimensions=grid_dimensions))
            for number_index in number_position
        )
    )

    adjacent_characters = [
        grid[adjacency_square_row][adjacency_square_column]
        for (adjacency_square_row, adjacency_square_column) in adjacency_squares
    ]

    return any(is_symbol_function(character) for character in adjacent_characters)

def part1(grid: typing.List[str]) -> int:
    numbers, number_positions = locate_numbers(grid=grid)

    return sum(
        number
        for number, number_position in zip(numbers, number_positions) 
        if is_adjacent_to_symbol_in_grid(grid=grid, number_position=number_position)
    )


def part2(grid: typing.List[str]) -> int:
    grid_dimensions = len(grid), len(grid[0])

    numbers, number_positions = locate_numbers(grid=grid)

    # NOTE: Generate mapping of number to all grid indices at which the number occurs.
    number_to_indices = defaultdict(list)

    for number, number_position in zip(numbers, number_positions):
        for index in number_position:
            number_to_indices[number].append(index)

    gear_ratio_sum = 0

    for star_symbol_index in generate_symbol_positions(grid=grid, is_symbol_function=lambda character: character == "*"):
        adjacent_positions = set(
            get_adjacent_indices(
                index=star_symbol_index, dimensions=grid_dimensions
            )
        )

        adjacent_numbers = [
            number
            for number, number_indices in number_to_indices.items()
            if adjacent_positions.intersection(number_indices)
        ]

        if len(adjacent_numbers) == 2:
            first_adjacent_number, second_adjacent_number = adjacent_numbers
            gear_ratio = first_adjacent_number * second_adjacent_number
            gear_ratio_sum += gear_ratio

    return gear_ratio_sum


def main():
    input_filepath = Path(__file__).parent.joinpath("data", "data.txt")
    grid = list(generate_inputs(input_filepath))

    print("PART1:", part1(grid=grid))
    print("PART2:", part2(grid=grid))

if __name__ == "__main__":
    main()

