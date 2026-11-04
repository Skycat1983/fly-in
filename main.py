#!/usr/bin/env python3
"""Command-line entry point for the drone routing program."""

from pathlib import Path
import sys

from fleet_planner import FleetPlanner
from graph import Graph
from parse import InputFormatError, InputParser
from route_finder import RouteFinder


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

    try:
        candidates = route_finder.find_candidate_paths()
        turn_lines = FleetPlanner(map_data, graph).choose_schedule(candidates)
    except (ValueError, NotImplementedError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    for line in turn_lines:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
