"""Tests for shortest-route discovery and reconstruction."""

from pathlib import Path
import unittest

from graph import Graph
from parse import (
    Connection,
    Hub,
    HubKind,
    HubMetadata,
    InputParser,
    MapDefinition,
    Position,
    ZoneKind,
)
from route_finder import RouteFinder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LINEAR_MAP = PROJECT_ROOT / "maps" / "easy" / "01_linear_path.txt"


def make_hub(
    kind: HubKind,
    name: str,
    zone: ZoneKind = ZoneKind.NORMAL,
) -> Hub:
    """Create a hub with only the route-relevant metadata varied."""

    return Hub(
        kind=kind,
        name=name,
        position=Position(0, 0),
        metadata=HubMetadata(zone=zone),
    )


def make_map(
    hubs: tuple[Hub, ...],
    connections: tuple[Connection, ...],
    *,
    start_name: str = "start",
    end_name: str = "end",
) -> MapDefinition:
    """Create a one-drone map with named start and end hubs."""

    return MapDefinition(
        drone_count=1,
        start_hub=make_hub(HubKind.START, start_name),
        hubs=hubs,
        end_hub=make_hub(HubKind.END, end_name),
        connections=connections,
    )


class RouteFinderTests(unittest.TestCase):
    """Verify shortest-path search and start-to-end reconstruction."""

    def test_movement_cost_reflects_each_zone_kind(self) -> None:
        """Zone costs should be testable independently from graph search."""

        expected_costs = {
            ZoneKind.NORMAL: 1,
            ZoneKind.PRIORITY: 1,
            ZoneKind.RESTRICTED: 2,
            ZoneKind.BLOCKED: None,
        }

        for zone, expected in expected_costs.items():
            with self.subTest(zone=zone):
                self.assertEqual(
                    RouteFinder._movement_cost(zone),
                    expected,
                )

    def test_linear_route_is_returned_from_start_to_end(self) -> None:
        """The bundled linear map should produce a forward route."""

        map_data = InputParser(LINEAR_MAP).parse()

        route = RouteFinder(Graph(map_data)).find_shortest_path()

        self.assertEqual(
            route,
            ["start", "waypoint1", "waypoint2", "goal"],
        )

    def test_end_hub_does_not_need_to_be_named_goal(self) -> None:
        """Route reconstruction should use the parsed end-hub name."""

        map_data = make_map(
            (),
            (Connection("origin", "destination"),),
            start_name="origin",
            end_name="destination",
        )

        route = RouteFinder(Graph(map_data)).find_shortest_path()

        self.assertEqual(route, ["origin", "destination"])

    def test_disconnected_destination_returns_empty_route(self) -> None:
        """An unreachable end hub should be represented by an empty list."""

        route = RouteFinder(Graph(make_map((), ()))).find_shortest_path()

        self.assertEqual(route, [])

    def test_blocked_hub_is_not_used(self) -> None:
        """A path whose only intermediate hub is blocked is unreachable."""

        blocked = make_hub(HubKind.REGULAR, "blocked", ZoneKind.BLOCKED)
        map_data = make_map(
            (blocked,),
            (
                Connection("start", "blocked"),
                Connection("blocked", "end"),
            ),
        )

        route = RouteFinder(Graph(map_data)).find_shortest_path()

        self.assertEqual(route, [])

    def test_entering_restricted_hub_costs_two_turns(self) -> None:
        """Restricted-zone entry should add two to the shortest distance."""

        restricted = make_hub(
            HubKind.REGULAR,
            "restricted",
            ZoneKind.RESTRICTED,
        )
        map_data = make_map(
            (restricted,),
            (
                Connection("start", "restricted"),
                Connection("restricted", "end"),
            ),
        )
        finder = RouteFinder(Graph(map_data))

        route = finder.find_shortest_path()

        self.assertEqual(route, ["start", "restricted", "end"])
        self.assertEqual(finder.distances["restricted"], 2)
        self.assertEqual(finder.distances["end"], 3)

    def test_equal_cost_routes_are_selected_consistently(self) -> None:
        """Heap ordering should make repeated equal-cost searches stable."""

        alpha = make_hub(HubKind.REGULAR, "alpha")
        beta = make_hub(HubKind.REGULAR, "beta")
        map_data = make_map(
            (beta, alpha),
            (
                Connection("start", "beta"),
                Connection("beta", "end"),
                Connection("start", "alpha"),
                Connection("alpha", "end"),
            ),
        )

        routes = [
            RouteFinder(Graph(map_data)).find_shortest_path()
            for _ in range(3)
        ]

        self.assertEqual(
            routes,
            [["start", "alpha", "end"]] * 3,
        )


if __name__ == "__main__":
    unittest.main()
