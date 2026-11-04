"""Tests for one drone moving along a normal-zone route."""

from pathlib import Path
import unittest

from graph import Graph
from parse import InputParser
from route_finder import RouteFinder
from simulator import Drone


LINEAR_MAP = (
    Path(__file__).resolve().parents[1]
    / "maps" / "easy" / "01_linear_path.txt"
)
RESTRICTED_MAP = (
    Path(__file__).resolve().parents[1]
    / "examples" / "one_drone_restricted.txt"
)


class DroneTests(unittest.TestCase):
    """Check route progress, position, and delivery for a single drone."""

    def test_normal_route_moves_once_per_turn_and_stops(self) -> None:
        """Each call advances one hub and delivery produces no extra move."""

        graph = Graph(InputParser(LINEAR_MAP).parse())
        path = RouteFinder(graph).find_shortest_path()
        drone = Drone(graph, 1)

        self.assertIs(drone.location, graph.get_hub("start"))
        self.assertEqual(drone.route_index, 0)

        for index, name in enumerate(("waypoint1", "waypoint2", "goal"), 1):
            with self.subTest(turn=index):
                self.assertEqual(drone.move_one_turn(path), name)
                self.assertEqual(drone.route_index, index)
                self.assertIs(drone.location, graph.get_hub(name))

        self.assertIsNone(drone.move_one_turn(path))
        self.assertEqual(drone.route_index, 3)
        self.assertIs(drone.location, graph.get_hub("goal"))

    def test_restricted_arrival_uses_connection_then_hub(self) -> None:
        """Transit keeps the route index at the source until next turn."""

        graph = Graph(InputParser(RESTRICTED_MAP).parse())
        path = RouteFinder(graph).find_shortest_path()
        drone = Drone(graph, 1)

        self.assertEqual(drone.move_one_turn(path), "start-restricted")
        self.assertIs(
            drone.location,
            graph.get_connection("start", "restricted"),
        )
        self.assertEqual(drone.route_index, 0)
        self.assertIs(drone.in_transit_to, graph.get_hub("restricted"))

        self.assertEqual(drone.move_one_turn(path), "restricted")
        self.assertIs(drone.location, graph.get_hub("restricted"))
        self.assertEqual(drone.route_index, 1)
        self.assertIsNone(drone.in_transit_to)

        self.assertEqual(drone.move_one_turn(path), "goal")
        self.assertEqual(drone.route_index, 2)
        self.assertIsNone(drone.move_one_turn(path))


if __name__ == "__main__":
    unittest.main()
