"""Tests for graph construction and topology lookups."""

from pathlib import Path
import unittest

from graph import Graph
from parse import HubKind, InputParser, Position


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMPLE_FORK_MAP = PROJECT_ROOT / "maps" / "easy" / "02_simple_fork.txt"


class GraphTests(unittest.TestCase):
    """Verify graph lookups using the simple-fork map."""

    def setUp(self) -> None:
        """Parse the simple-fork map and build its graph."""

        map_data = InputParser(SIMPLE_FORK_MAP).parse()
        self.graph = Graph(map_data)

    def test_get_hub_returns_junction(self) -> None:
        """Looking up junction returns its complete parsed hub."""

        junction = self.graph.get_hub("junction")

        self.assertEqual(junction.name, "junction")
        self.assertIs(junction.kind, HubKind.REGULAR)
        self.assertEqual(junction.position, Position(1, 0))
        self.assertEqual(junction.metadata.max_drones, 2)

    def test_get_neighbours_returns_all_junction_neighbours(self) -> None:
        """Junction is adjacent to the start and both fork paths."""

        neighbour_names = [
            hub.name
            for hub in self.graph.get_neighbours("junction")
        ]

        self.assertEqual(neighbour_names, ["start", "path_a", "path_b"])

    def test_connection_can_be_looked_up_in_both_directions(self) -> None:
        """Both endpoint orders return the same undirected connection."""

        forward = self.graph.get_connection("start", "junction")
        reverse = self.graph.get_connection("junction", "start")

        self.assertIs(forward, reverse)
        self.assertEqual(forward.source, "start")
        self.assertEqual(forward.destination, "junction")

    def test_connection_retains_its_capacity(self) -> None:
        """Graph storage preserves parsed connection metadata."""

        connection = self.graph.get_connection("start", "junction")

        self.assertEqual(connection.metadata.max_link_capacity, 2)


if __name__ == "__main__":
    unittest.main()
