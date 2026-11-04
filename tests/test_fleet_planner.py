"""Tests for choosing a fleet schedule from candidate routes."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from fleet_planner import FleetPlanner
from graph import Graph
from main import main
from parse import InputParser
from route_finder import RouteFinder
from simulator import Simulator


FORK_MAP = (
    Path(__file__).resolve().parents[1]
    / "maps" / "easy" / "02_simple_fork.txt"
)
FORK_OUTPUT = [
    "D1-junction D2-junction",
    "D1-path_a D2-path_b D3-junction D4-junction",
    "D1-goal D2-goal D3-path_a D4-path_b",
    "D3-goal D4-goal",
]


class FleetPlannerTests(unittest.TestCase):
    """Check the first automatic route-assignment policy."""

    def test_spreading_fork_drones_beats_shared_route(self) -> None:
        """The planner chooses four turns instead of the six-turn queue."""

        map_data = InputParser(FORK_MAP).parse()
        graph = Graph(map_data)
        candidates = RouteFinder(graph).find_candidate_paths()
        shared = Simulator(map_data, graph).traverse(candidates[0])

        self.assertEqual(len(shared), 6)
        self.assertEqual(
            FleetPlanner(map_data, graph).choose_schedule(candidates),
            FORK_OUTPUT,
        )

    def test_cli_uses_both_fork_branches(self) -> None:
        """The CLI prints the selected four-turn schedule."""

        output = StringIO()
        with patch("sys.argv", ["main.py", str(FORK_MAP)]):
            with redirect_stdout(output):
                exit_code = main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), "\n".join(FORK_OUTPUT) + "\n")


if __name__ == "__main__":
    unittest.main()
