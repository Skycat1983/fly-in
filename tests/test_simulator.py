"""Tests for simultaneous turn output and capacity limits."""

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from graph import Graph
from main import main
from parse import InputParser
from route_finder import RouteFinder
from simulator import Simulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ONE_DRONE_MAP = PROJECT_ROOT / "examples" / "one_drone_linear.txt"
RESTRICTED_MAP = PROJECT_ROOT / "examples" / "one_drone_restricted.txt"
TWO_DRONE_MAP = PROJECT_ROOT / "maps" / "easy" / "01_linear_path.txt"
FORK_MAP = PROJECT_ROOT / "maps" / "easy" / "02_simple_fork.txt"
WIDE_ROUTE_MAP = PROJECT_ROOT / "tests" / "fixtures" / "wide_route.txt"


class SimulatorTests(unittest.TestCase):
    """Verify movement lines, turn counts, and shared-route scheduling."""

    def test_one_drone_finishes_in_three_turns(self) -> None:
        """The simulator emits the destination of each move, then stops."""

        map_data = InputParser(ONE_DRONE_MAP).parse()
        graph = Graph(map_data)
        route = RouteFinder(graph).find_shortest_path()
        simulator = Simulator(map_data, graph)

        self.assertEqual(
            simulator.traverse(route),
            ["D1-waypoint1", "D1-waypoint2", "D1-goal"],
        )
        self.assertEqual(simulator.turn_counter, 3)

    def test_cli_prints_only_turn_lines(self) -> None:
        """A one-drone map produces the exact required movement format."""

        output = StringIO()
        with patch("sys.argv", ["main.py", str(ONE_DRONE_MAP)]):
            with redirect_stdout(output):
                exit_code = main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue(),
            "D1-waypoint1\nD1-waypoint2\nD1-goal\n",
        )

    def test_restricted_route_has_connection_and_arrival_turns(self) -> None:
        """A restricted arrival emits two lines and counts two turns."""

        map_data = InputParser(RESTRICTED_MAP).parse()
        graph = Graph(map_data)
        route = RouteFinder(graph).find_shortest_path()
        simulator = Simulator(map_data, graph)

        self.assertEqual(
            simulator.traverse(route),
            ["D1-start-restricted", "D1-restricted", "D1-goal"],
        )
        self.assertEqual(simulator.turn_counter, 3)

    def test_two_drones_share_linear_route_in_four_turns(self) -> None:
        """A departing drone frees its hub for the follower that turn."""

        map_data = InputParser(TWO_DRONE_MAP).parse()
        graph = Graph(map_data)
        route = RouteFinder(graph).find_shortest_path()
        simulator = Simulator(map_data, graph)
        expected = [
            "D1-waypoint1",
            "D1-waypoint2 D2-waypoint1",
            "D1-goal D2-waypoint2",
            "D2-goal",
        ]

        self.assertEqual(simulator.traverse(route), expected)
        self.assertEqual(simulator.turn_counter, 4)

    def test_assigned_fork_routes_finish_in_four_turns(self) -> None:
        """All drones share capacity checks while using two branch routes."""

        map_data = InputParser(FORK_MAP).parse()
        graph = Graph(map_data)
        route_a = ["start", "junction", "path_a", "goal"]
        route_b = ["start", "junction", "path_b", "goal"]
        simulator = Simulator(map_data, graph)

        self.assertEqual(
            simulator.traverse_routes({
                1: route_a, 2: route_b, 3: route_a, 4: route_b,
            }),
            [
                "D1-junction D2-junction",
                "D1-path_a D2-path_b D3-junction D4-junction",
                "D1-goal D2-goal D3-path_a D4-path_b",
                "D3-goal D4-goal",
            ],
        )
        self.assertEqual(simulator.turn_counter, 4)

    def test_each_drone_requires_an_assigned_route(self) -> None:
        """A missing assignment fails before simulation starts."""

        map_data = InputParser(FORK_MAP).parse()
        simulator = Simulator(map_data, Graph(map_data))

        with self.assertRaisesRegex(ValueError, "Each drone needs"):
            simulator.traverse_routes({
                1: ["start", "junction", "path_a", "goal"],
            })

    def test_cli_prints_four_turns_for_supplied_linear_map(self) -> None:
        """The CLI prints all drones' accepted moves on each turn."""

        output = StringIO()
        error_output = StringIO()
        with patch("sys.argv", ["main.py", str(TWO_DRONE_MAP)]):
            with redirect_stdout(output), redirect_stderr(error_output):
                exit_code = main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(error_output.getvalue(), "")
        self.assertEqual(
            output.getvalue(),
            "D1-waypoint1\n"
            "D1-waypoint2 D2-waypoint1\n"
            "D1-goal D2-waypoint2\n"
            "D2-goal\n",
        )

    def test_higher_capacities_allow_two_drones_in_one_hub(self) -> None:
        """Hub and link capacities of two permit two moves per turn."""

        map_data = InputParser(WIDE_ROUTE_MAP).parse()
        graph = Graph(map_data)
        route = RouteFinder(graph).find_shortest_path()
        simulator = Simulator(map_data, graph)

        self.assertEqual(
            simulator.traverse(route),
            ["D1-lane D2-lane", "D1-goal D2-goal D3-lane", "D3-goal"],
        )
        self.assertEqual(simulator.turn_counter, 3)

    def test_restricted_arrival_reserves_hub_and_link(self) -> None:
        """A follower waits while the leader must arrive from transit."""

        map_data = replace(InputParser(RESTRICTED_MAP).parse(), drone_count=2)
        graph = Graph(map_data)
        route = RouteFinder(graph).find_shortest_path()
        simulator = Simulator(map_data, graph)

        self.assertEqual(
            simulator.traverse(route),
            [
                "D1-start-restricted",
                "D1-restricted",
                "D1-goal D2-start-restricted",
                "D2-restricted",
                "D2-goal",
            ],
        )
        self.assertEqual(simulator.turn_counter, 5)


if __name__ == "__main__":
    unittest.main()
