#!/usr/bin/env python3
"""Command-line entry point for the drone routing program."""

from pathlib import Path
import sys

from formatting import format_movement
from graph import Graph, MapDefinition
from parse import (
    InputFormatError,
    InputParser,
    Connection,
    Hub,
    ZoneKind,
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


class Drone:
    """Track one drone's position along a planned route."""

    def __init__(self, graph: Graph, drone_id: int) -> None:
        """Place a numbered drone at the map's start hub."""

        self.graph = graph
        self.drone_id: int = drone_id
        self.location: Hub | Connection = graph.map_data.start_hub
        self.route_index: int = 0

    def get_id(self) -> int:
        """Return this drone's identifier."""

        return self.drone_id

    def move_one_turn(self, path: list[str]) -> str | None:
        """Move one normal step and return its hub name.

        Return None if the drone has reached the end of the route.
        """

        if not path:
            raise ValueError("A drone cannot move without a route")

        if self.route_index == len(path) - 1:
            return None

        next_index = self.route_index + 1
        destination = self.graph.get_hub(path[next_index])
        if destination.metadata.zone is ZoneKind.RESTRICTED:
            raise NotImplementedError(
                "Restricted-zone transit is not implemented"
            )

        self.route_index = next_index
        self.location = destination
        return destination.name


class Simulator:
    """Advance drones through routes one turn at a time."""

    def __init__(self,
                 map_data: MapDefinition,
                 graph: Graph) -> None:
        """Keep the map, graph, and count of completed turns."""

        self.map_data = map_data
        self.graph = graph
        self.turn_counter = 0

    def traverse(self, path: list[str]) -> list[str]:
        """Return one output line per turn for a single normal-route drone."""

        if self.map_data.drone_count != 1:
            raise ValueError("Only one drone is supported by the simulator")
        if not path:
            raise ValueError("No route reaches the end hub")

        drone = Drone(self.graph, 1)
        turn_lines: list[str] = []
        while True:
            destination = drone.move_one_turn(path)
            if destination is None:
                break
            self.turn_counter += 1
            turn_lines.append(format_movement(drone.get_id(), destination))

        return turn_lines


def main() -> int:
    """Parse a map and print each completed simulation turn."""

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

    graph = Graph(map_data)
    route_finder = RouteFinder(graph)
    shortest_path = route_finder.find_shortest_path()
    simulator = Simulator(map_data, graph)

    try:
        turn_lines = simulator.traverse(shortest_path)
    except (ValueError, NotImplementedError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    for line in turn_lines:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
