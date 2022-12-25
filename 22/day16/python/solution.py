from collections import namedtuple
import itertools
from pathlib import Path
import re
import typing

import igraph
from igraph import Graph
import numpy as np
import matplotlib.pyplot as plt

pattern = r"Valve (?P<name>[A-Z][A-Z]) has flow rate=(?P<rate>[0-9]+); tunnels? leads? to valves? (?P<connected_valves>([A-Z][A-Z],? ?)+)"

# NOTE: Tuple of valve index visiting order and corresponding pressure released score.
ScoredOrder = namedtuple("ScoredOrder", field_names=["order", "score"])


def parse_lines(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Tuple[
    typing.List[str], typing.List[int], typing.List[typing.Tuple[str, str]]
]:
    """Extract valve names, rates and edges from the raw input.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Input file containing all valve definitions.

    Returns
    -------
    valve_names: typing.List[str]
        Names of the valves, serves as index into the other two lists.
    valve_rates: typing.List[int]
        Rates for each of the valves, sorted in the same order as `valve_names`.
    valve_edges: typing.List[int]
        Tuples `(valve_1, valve_2)` that indicate presence of a tunnel/edge between
        the two valves.
    """
    valve_names = []
    valve_rates = []
    valve_edges = []
    with open(filepath, "r") as inputs_file:
        for line in inputs_file:
            match = re.search(string=line, pattern=pattern)

            if match:
                name = match.group("name")
                rate = int(match.group("rate"))
                connected_valves = match.group("connected_valves").split(", ")

                valve_names.append(name)
                valve_rates.append(rate)

                for connected_valve in connected_valves:
                    valve_edges.append((name, connected_valve))
            else:
                raise ValueError(f"Ill-formatted line: {line}")

        valve_name_to_index = lambda name: valve_names.index(name)

        valve_id_edges = [
            (valve_name_to_index(edge[0]), valve_name_to_index(edge[1]))
            for edge in valve_edges
        ]

        connectivity_graph = Graph(
            n=len(valve_names),
            edges=valve_id_edges,
            directed=True,
        )
        connectivity_graph.vs["name"] = list(valve_names)
        connectivity_graph.vs["rate"] = list(valve_rates)

        # NOTE: Deactivated connectivity visualization
        # _plot_graph(connectivity_graph)
        return valve_names, valve_rates, connectivity_graph


def _plot_graph(connectivity_graph: Graph) -> None:
    """Visualize valve graph where edges indicate tunnels and labels indicate
       names and rates.

       Was used to visualize what's going on intermediately.
       Not part of final solution.

    Parameters
    ----------
    connectivity_graph : igraph.Graph
        Graph representing the interaction between valves (via tunnels).

    """
    fig, ax = plt.subplots(figsize=(5, 5))
    igraph.plot(
        connectivity_graph,
        target=ax,
        layout="circle",  # print nodes in a circular layout
        vertex_label=g.vs["name"],
    )
    plt.show()


def process_visiting_order(
    distances: np.ndarray,
    valve_order: typing.List[str],
    valve_rates: typing.List[int],
    start_valve: int = 0,
    time_left: int = 31,
) -> int:
    """Process a given visiting order of the valves, returning total pressure released.

    Parameters
    ----------
    distances : np.ndarray
        2d-distance matrix between valves (by valve index).
    valve_order : typing.List[int]
        Order to process valves by (list of valve indices).
    valve_rates: typing.List[int]
        Rates for each of the valves (by corresponding valve index).
    start_valve: int, optional
        Index of start valve to process visiting order from. Default: `0`.
    time_left: int, optional
        Number of minutes left when starting to process. Default: `30`.

    Returns
    -------
    total_pressure_released: int
        Total pressure released at the end of processing all valve nodes.
    """
    pressure_released = 0
    current_valve = int(start_valve)

    for next_valve in valve_order:
        travel_time = distances[current_valve][next_valve]
        time_left -= travel_time
        time_left -= 1  # Subtract time to open the valve!

        pressure_released += time_left * valve_rates[next_valve]

        current_valve = int(next_valve)

    return pressure_released


def recursively_generate_visiting_orders(
    distances: np.ndarray,
    start_valve: int,
    valves_left_to_visit: typing.Set[int],
    valves_visited: typing.List[int],
    time_left: int = 31,
) -> typing.Iterable[typing.List[int]]:
    """Generate all possible visiting orders of valve nodes, recursively.

    Parameters
    ----------
    distances : np.ndarray
        2d-distance matrix between valves (by valve index).
    start_valve : int
        Index of valve to start visiting valves from.
    valves_left_to_visit : typing.Set[int]
        Set of valves not yet visited that neighbors are picked from.
    valves_visited : typing.List
        Valves visited previously.
        This is maintained and yielded to generate combinations.
    time_left: int, optional
        Number of minutes left. Default: `30`.

    Yields
    ------
    visiting_order: typing.List[int]
        Indices of valves to visit; sorting order indicates order to visit them in.
    """
    for valve_to_visit in valves_left_to_visit:
        travel_time = distances[start_valve][valve_to_visit]

        if (travel_time + 1) < time_left:  # Include time to open valve...
            yield from recursively_generate_visiting_orders(
                distances=distances,
                start_valve=valve_to_visit,
                valves_left_to_visit=valves_left_to_visit - set((valve_to_visit,)),
                valves_visited=valves_visited + [valve_to_visit],
                time_left=time_left - (travel_time + 1),
            )

    yield valves_visited


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    start_valve_name: str = "AA",
    time_left_at_start: int = 30,
) -> int:
    """Maximum pressure that can be released across all possible visiting orders
       of the valves.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Input file containing all valve definitions.
    start_valve_name: str, optional
        Name of start valve to start visiting and opening valves from.
        Default: `"AA"`.
    time_left_at_start: int, optional
        Amount of time (in minutes) available to visit and open valves.
        Default: `26`.

    Returns
    -------
    max_pressure_released: int
        Maximum pressure released across all possible visiting orders of the valves.
    """
    valve_names, valve_rates, connectivity_graph = parse_lines(filepath=filepath)
    distances = connectivity_graph.shortest_paths()

    relevant_valves = {
        valve_index
        for valve_index in range(len(valve_names))
        if valve_rates[valve_index]
        > 0  # NOTE: Valves with rate 0 never contribute, so just drop them
    }

    visiting_orders = recursively_generate_visiting_orders(
        distances=distances,
        start_valve=valve_names.index(start_valve_name),
        valves_left_to_visit=relevant_valves,
        valves_visited=[],
        time_left=time_left_at_start,
    )

    return max(
        process_visiting_order(
            distances=distances,
            valve_order=visiting_order,
            valve_rates=valve_rates,
            start_valve=valve_names.index(start_valve_name),
            time_left=time_left_at_start,
        )
        for visiting_order in visiting_orders
    )


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    start_valve_name: str = "AA",
    time_left_at_start: int = 26,
) -> int:
    """Best pressure released score that can be achieved in team work with an elephant.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Input file containing all valve definitions.
    start_valve_name: str, optional
        Name of start valve to start visiting and opening valves from.
        Default: `"AA"`.
    time_left_at_start: int, optional
        Amount of time (in minutes) available to visit and open valves.
        Default: `26`.

    Returns
    -------
    best_score: int
        Best pressure released score that can be achieved when visiting nodes
        with two pointers (me and the elephant).
    """
    valve_names, valve_rates, connectivity_graph = parse_lines(filepath=filepath)
    distances = connectivity_graph.shortest_paths()

    relevant_valves = {
        valve_index
        for valve_index in range(len(valve_names))
        if valve_rates[valve_index]
        > 0  # NOTE: Valves with rate 0 never contribute, so just drop them
    }

    visiting_orders = recursively_generate_visiting_orders(
        distances=distances,
        start_valve=valve_names.index(start_valve_name),
        valves_left_to_visit=relevant_valves,
        valves_visited=[],
        time_left=time_left_at_start,
    )

    orders_with_scores = [
        ScoredOrder(
            order=visiting_order,
            score=process_visiting_order(
                distances=distances,
                valve_order=visiting_order,
                valve_rates=valve_rates,
                start_valve=valve_names.index(start_valve_name),
                time_left=time_left_at_start,
            ),
        )
        for visiting_order in visiting_orders
    ]

    best_score = float("-inf")

    for scored_order_human, scored_order_elephant in itertools.combinations(
        # NOTE: Slightly dirty efficiency hack. Sort by score descending,
        # this allows us to find the score faster by stopping once the best found
        # score exceeds 2 * human score (as human score starts at maximal value)
        sorted(
            orders_with_scores,
            key=lambda scored_order: scored_order.score,
            reverse=True,
        ),
        r=2,
    ):

        if (scored_order_human.score * 2) < best_score:
            break

        if set(scored_order_human.order).intersection(scored_order_elephant.order):
            # NOTE: Ensure human and elephant don't try to open the same valves.
            continue

        combined_score = scored_order_human.score + scored_order_elephant.score

        best_score = max(best_score, combined_score)

    return best_score


def main():
    print("Part 1:", part_1())
    print("Part 2:", part_2())


if __name__ == "__main__":
    main()
