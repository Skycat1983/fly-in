#!/usr/bin/env python3
"""Command-line entry point for the drone routing program."""

from pathlib import Path
import sys

from formatting import format_connection, format_hub  # noqa: F401
from graph import Graph, MapDefinition
from parse import (
    InputFormatError,
    InputParser,
)
from route_finder import RouteFinder

# normal – Standard zone with 1 turn movement cost (default)
# ◦ blocked – Inaccessible zone. Drones must not enter or pass
# through this zone. Any path using it is invalid.
# ◦ restricted – A sensitive or dangerous zone. Movement to this zone costs 2
# turns.
# ◦ priority – A preferred zone. Movement to this zone costs 1 turn but should
# be prioritized in pathfinding
# ! ./main.py "./maps/easy/01_linear_path.txt"

# ! Each movement between zones has a cost in turns, based on the zone=type of
# ! the destination:
# • normal: 1 turn (default)
# • restricted: 2 turns
# • priority: 1 turn (but should be preferred in pathfinding algorithms)
# • blocked: Inaccessible — cannot be entered


class Simulator:
    def __init__(self,
                 map_data: MapDefinition,
                 graph: Graph,
                 route_finder: RouteFinder) -> None:
        self.map_data = map_data
        self.graph = graph
        self.route_finder = route_finder
        self.turn_counter = 0
        pass

    def traverse(self, path: list[str]) -> None:
        # for name in path:
        #     print(name)
        #     location = graph
        pass


def main() -> int:
    """Parse the map supplied on the command line and display its data."""

    if len(sys.argv) != 2:
        program = Path(sys.argv[0]).name

        print(
            f"Usage: {program} PATH_TO_MAP_FILE",
            file=sys.stderr,
        )

        return 2

    path = Path(sys.argv[1])

    try:
        map_data = InputParser(path).parse()
    except (OSError, UnicodeError, InputFormatError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Drones: {map_data.drone_count}")
    print(f"Start: {map_data.start_hub.name}")
    print(f"End: {map_data.end_hub.name}")

    print()

    graph = Graph(map_data)
    route_finder = RouteFinder(graph)
    shortest_path = route_finder.find_shortest_path()
    # print("path = ", shortest_path)
    simulator = Simulator(map_data, graph, route_finder)
    simulator.traverse(shortest_path)
# - Is an empty list sufficiently clear for an unreachable destination, or will
#   callers need a more descriptive result later?
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
