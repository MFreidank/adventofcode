from pathlib import Path
import typing


def get_inputs(
    filepath: Path, ignore_spaces: bool = False
) -> typing.Tuple[typing.List[int], typing.List[int]]:
    """Get input from the given file, as a tuple of lists of race times and distances.

    Parameters:
    -----------
    filepath (pathlib.Path):
        Read inputs from the given filepath.
    ignore_spaces (bool, optional):
        Whether to assume a bad kerning of the paper with the race card.
        If set to `True` spaces between distance and time specifications are ignored.
        Default: `False`.

    Returns:
    --------
    times (typing.List[int]):
        Times of each race, corresponding to distance by index.
    distances (typing.List[int]):
        Distance travelled in each race, corresponding to time by index.
    """
    with open(filepath, "r") as f:
        line_iterator = iter(f)
        time_line = next(line_iterator)
        _, time_str = time_line.split(":")

        if ignore_spaces:
            times = [int("".join(time_str.strip().replace(" ", "")))]
        else:
            times = [int(time) for time in time_str.strip().split()]

        distance_line = next(line_iterator)
        _, distance_str = distance_line.split(":")

        if ignore_spaces:
            distances = [int(distance_str.strip().replace(" ", ""))]
        else:
            distances = [int(distance) for distance in distance_str.strip().split()]
    return times, distances


def num_ways_to_win(time: int, recorded_distance: int) -> int:
    """Determine the number of ways to win the race, i.e., to beat `recorded_distance`.

    Parameters:
    -----------
    time (int):
        Race time.
    recorded_distance (int):
        Recorded race distance travelled in `race_time`.
        Must be beaten to win the race.

    Returns:
    --------
    num_ways_to_beat_recorded_distance (int):
        Number of ways to use button presses to win the race.
    """
    speeds = range(0, time + 1)

    num_wins = 0

    for speed, time in zip(speeds, reversed(speeds)):
        travelled_distance = speed * time
        if travelled_distance > recorded_distance:
            num_wins += 1

    return num_wins


def part1(filepath: Path) -> int:
    """Multiple races, one for each distance/time pair in the inputs (separated by spaces)."""
    times, recorded_distances = get_inputs(filepath, ignore_spaces=False)

    multiplication_result = 1
    for time, recorded_distance in zip(times, recorded_distances):
        multiplication_result *= num_ways_to_win(
            time=time, recorded_distance=recorded_distance
        )

    return multiplication_result


def part2(filepath: Path) -> int:
    """A single race, defined as a single distance/time pair (ignoring all spaces between distances and times)."""
    times, recorded_distances = get_inputs(filepath, ignore_spaces=True)

    multiplication_result = 1
    for time, recorded_distance in zip(times, recorded_distances):
        multiplication_result *= num_ways_to_win(
            time=time, recorded_distance=recorded_distance
        )

    return multiplication_result


def main():
    filepath = Path(__file__).parent.joinpath("data", "data.txt")
    print("PART 1:", part1(filepath=filepath))
    print("PART 2:", part2(filepath=filepath))


if __name__ == "__main__":
    main()
