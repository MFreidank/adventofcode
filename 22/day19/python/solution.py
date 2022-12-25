from collections import defaultdict
from functools import reduce
from itertools import islice
import logging
from pathlib import Path
import re
import typing

import pulp

# NOTE: Regex patterns to extract fields during parsing.
blueprint_id_pattern = re.compile(r"Blueprint (?P<blueprint_id>[0-9]+):")
robot_type_pattern = re.compile(r"(?P<robot_type>(ore|clay|obsidian|geode)) robot")
robot_costs_pattern = re.compile("(?P<amount>[0-9]+) (?P<resource>ore|clay|obsidian)")


def generate_inputs(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[typing.Tuple[int, typing.Dict[str, typing.Dict[str, int]]]]:
    """Generate tuples of blueprint ID and corresponding robot costs for a given blueprint.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file to inpute to generate blueprints  from.

    Yields
    ------
    blueprint_id: int
        Integer blueprint ID.
    blueprint_robot_costs: typing.Dict[str, typing.Dict[str, int]]
        Mapping of costs to construct robots of a given resource type.
        Outer keys are resources for the robot, inner keys are resources required
        for construction and are mapped to an amount of this resource that is needed.
    """
    with open(filepath, "r") as inputs_file:
        line_iterator = iter(inputs_file)

        while True:
            try:
                line = next(line_iterator)
            except StopIteration:
                break
            robot_costs = defaultdict(lambda: dict())
            blueprint_id_match = re.match(
                pattern=blueprint_id_pattern, string=line.strip()
            )
            if blueprint_id_match:
                blueprint_id = int(blueprint_id_match.group("blueprint_id"))

            lines = line.split(".")
            for robot_line in line.split("."):
                robot_type_match = re.search(
                    pattern=robot_type_pattern, string=robot_line
                )
                if robot_type_match:
                    robot_type = robot_type_match.group("robot_type")

                robot_costs_match = re.findall(
                    pattern=robot_costs_pattern, string=robot_line
                )

                for (amount, resource) in robot_costs_match:
                    robot_costs[robot_type][resource] = int(amount)

            yield blueprint_id, robot_costs


def maximum_resource_after_num_minutes(
    robot_costs: typing.Dict[str, typing.Dict[str, int]],
    num_minutes_to_simulate: int = 24,
    optimize_direction=pulp.LpMaximize,
    resource_to_optimize="geode",
) -> int:
    """Determines the optimal (e.g., maximal) amount of geodes that can be opened in
       a given number of minutes, when robots for the different resources have given costs.

       Internally constructs a linear program using `pulp` to model the state changes.

    Parameters
    ----------
    robot_costs : typing.Dict[str, typing.Dict[str, int]]
        Mapping of costs to construct robots of a given resource type.
        Outer keys are resources for the robot, inner keys are resources required
        for construction and are mapped to an amount of this resource that is needed.
    num_minutes_to_simulate: int, optional
        Number of minutes to simulate. Default: `24`.
    optimize_direction: int, optional
        Whether to maximize or minimize the objective resource when solving the
        linear program.
    resource_to_optimize: str, optional
        Resource to optimize at the end of the simulation. Default: `"geode"`

    Returns
    -------
    optimal_resource_count: int
        Optimal resource count that can be achieved given the problem specification.
    """
    num_minutes = num_minutes_to_simulate + 1  # count starts at 0

    pulp_problem = pulp.LpProblem(
        name="maximize_open_geodes",
        sense=optimize_direction,
    )

    resources = tuple(robot_costs.keys())

    # NOTE: Construct integer variables for available resources, harvesting robots
    # and robot construction at any point in time during the simulation.
    resource_variables = {
        resource: [
            pulp.LpVariable(
                name=f"{resource}_available_at_minute_{minutes}",
                lowBound=0,
                # Initially all resources are fixed to 0
                upBound=0 if minutes == 0 else None,
                cat=pulp.LpInteger,
            )
            for minutes in range(num_minutes)
        ]
        for resource in resources
    }
    num_robots_variables = {
        resource: [
            pulp.LpVariable(
                name=f"num_robots_{resource}_at_minute_{minutes}",
                # Initially start with exactly one ore robot and
                # exactly 0 other robots
                lowBound={
                    (0, "ore"): 1,
                }.get((minutes, resource), 0),
                upBound={
                    (0, "ore"): 1,
                    (0, "clay"): 0,
                    (0, "obsidian"): 0,
                    (0, "geode"): 0,
                }.get((minutes, resource), None),
                cat=pulp.LpInteger,
            )
            for minutes in range(num_minutes)
        ]
        for resource in resources
    }
    construct_num_robots_variables = {
        resource: [
            pulp.LpVariable(
                name=f"construct_robots_{resource}_at_minute_{minutes}",
                lowBound=0,
                upBound=None,
                cat=pulp.LpInteger,
            )
            for minutes in range(num_minutes)
        ]
        for resource in resources
    }

    pulp_problem.addVariables(
        sum(
            (
                variables
                for variables in [
                    *resource_variables.values(),
                    *num_robots_variables.values(),
                    *construct_num_robots_variables.values(),
                ]
            ),
            [],
        )
    )

    # NOTE: Add constraints on the variables to ensure state transitions behave as intended.

    # At any time, we can construct at most one robot.
    for minute in range(num_minutes):
        pulp_problem.addConstraint(
            sum(
                (
                    construct_num_robots_variables[resource][minute]
                    for resource in resources
                )
            )
            <= 1
        )

    for current_minute, next_minute in zip(range(num_minutes), range(num_minutes)[1:]):
        for resource in resources:
            # We can only construct robots only if sufficient resources are available.
            pulp_problem.addConstraint(
                name=f"construct_robot_only_if_sufficient_{resource}_at_minute_{current_minute}",
                constraint=(
                    (
                        resource_variables[resource][current_minute]
                        - sum(
                            (
                                construct_num_robots_variables[robot_resource][
                                    current_minute
                                ]
                                * robot_costs[robot_resource].get(resource, 0)
                                for robot_resource in resources
                            )
                        )
                    )
                    >= 0
                ),
            )

            # Resources at time (t + 1) must be equal to resources at time t
            # plus resources harvested by robots minus resources spent
            # to create new robots.
            pulp_problem.addConstraint(
                name=f"update_{resource}_between_minutes_{current_minute}_{next_minute}",
                constraint=(
                    (
                        resource_variables[resource][next_minute]
                        == (
                            resource_variables[resource][current_minute]
                            + num_robots_variables[resource][current_minute]
                            - (
                                sum(
                                    construct_num_robots_variables[robot_resource][
                                        current_minute
                                    ]
                                    * robot_costs[robot_resource].get(resource, 0)
                                    for robot_resource in resources
                                )
                            )
                        )
                    )
                ),
            )

            # Robots at time (t + 1) must be equal to robots at time t
            # plus robots that were newly created.
            pulp_problem.addConstraint(
                name=f"update_num_{resource}_robots_between_minutes_{current_minute}_{next_minute}",
                constraint=(
                    num_robots_variables[resource][next_minute]
                    == (
                        num_robots_variables[resource][current_minute]
                        + construct_num_robots_variables[resource][current_minute]
                    )
                ),
            )

    # Set the resource to optimize as objective (at the end of simulation).
    pulp_problem.setObjective(resource_variables[resource_to_optimize][num_minutes - 1])

    _ = pulp_problem.solve()

    return int(pulp_problem.objective.value())


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    num_minutes_to_simulate: int = 24,
    resource_to_optimize: str = "geode",
    optimize_direction: int = pulp.LpMaximize,
) -> int:
    """Determine quality levels of blueprints as the maximum number of geodes that
       can be opened in `24` minutes.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file to inpute to generate blueprints  from.
    num_minutes_to_simulate: int, optional
        Number of minutes to simulate. Default: `24`.
    optimize_direction: int, optional
        Whether to maximize or minimize the objective resource when solving the
        linear program. Default: `pulp.LpMaximize`
    resource_to_optimize: str, optional
        Resource to optimize at the end of the simulation. Default: `"geode"`

    Returns
    -------
    quality_level_sum: int
        Sum of the quality levels of all blueprints.
    """

    return sum(
        (
            blueprint_id
            * maximum_resource_after_num_minutes(
                robot_costs=blueprint_robot_costs,
                num_minutes_to_simulate=num_minutes_to_simulate,
                resource_to_optimize=resource_to_optimize,
                optimize_direction=optimize_direction,
            )
            for blueprint_id, blueprint_robot_costs in generate_inputs(
                filepath=filepath
            )
        )
    )


def part_2(
    filepath=Path(__file__).parent.parent.joinpath("inputs.txt"),
    num_minutes_to_simulate: int = 32,
    num_blueprints_to_consider=3,
    resource_to_optimize: str = "geode",
    optimize_direction: int = pulp.LpMaximize,
) -> int:
    """Determine multiplication of first n blueprint qualities when
       simulating for `32` minutes.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Path to input file to inpute to generate blueprints  from.
    num_minutes_to_simulate: int, optional
        Number of minutes to simulate. Default: `32`.
    num_blueprints_to_consider: int, optional
        Number of blueprints to consider. Default: `3`, uses first three blueprints.
    optimize_direction: int, optional
        Whether to maximize or minimize the objective resource when solving the
        linear program. Default: `pulp.LpMaximize`
    resource_to_optimize: str, optional
        Resource to optimize at the end of the simulation. Default: `"geode"`

    Returns
    -------
    multiplied_blueprint_qualities: int
        Multiplication of (raw) quality values of first three blueprints.
    """
    return reduce(
        lambda x, y: x * y,
        (
            maximum_resource_after_num_minutes(
                robot_costs=blueprint_robot_costs,
                num_minutes_to_simulate=num_minutes_to_simulate,
                resource_to_optimize=resource_to_optimize,
                optimize_direction=optimize_direction,
            )
            for _, blueprint_robot_costs in islice(
                generate_inputs(filepath=filepath),
                num_blueprints_to_consider,
            )
        ),
        1,
    )


def main():
    print("Part 1:", part_1())
    print("Part 2:", part_2())


if __name__ == "__main__":
    main()
