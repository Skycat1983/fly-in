"""Tests for one-drone turn output and the command-line boundary."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from graph import Graph
from main import Simulator, main
from parse import InputParser
from route_finder import RouteFinder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ONE_DRONE_MAP = PROJECT_ROOT / "examples" / "one_drone_linear.txt"
TWO_DRONE_MAP = PROJECT_ROOT / "maps" / "easy" / "01_linear_path.txt"


class SimulatorTests(unittest.TestCase):
    """Verify one movement line per normal turn and explicit scope limits."""

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

    def test_cli_rejects_two_drones_until_scheduling_exists(self) -> None:
        """The program does not silently omit drones from a supplied map."""

        output = StringIO()
        error_output = StringIO()
        with patch("sys.argv", ["main.py", str(TWO_DRONE_MAP)]):
            with redirect_stdout(output), redirect_stderr(error_output):
                exit_code = main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("Only one drone", error_output.getvalue())


if __name__ == "__main__":
    unittest.main()
