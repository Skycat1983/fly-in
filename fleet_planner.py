"""Choose a fleet schedule from a small set of candidate routes."""

from graph import Graph, MapDefinition
from simulator import Simulator


class FleetPlanner:
    """Compare a shared route with a simple spread across candidates."""

    def __init__(self, map_data: MapDefinition, graph: Graph) -> None:
        """Keep the map and graph used by each trial simulation."""

        self.map_data = map_data
        self.graph = graph

    def choose_schedule(self, candidates: list[list[str]]) -> list[str]:
        """Return the valid trial with fewer completion turns.

        The shared plan gives every drone the first candidate. The spread
        plan assigns candidates in order, repeating when drones outnumber
        routes. A failed spread trial leaves the shared plan in use.
        """

        if not candidates:
            raise ValueError("No route reaches the end hub")

        shared = Simulator(self.map_data, self.graph).traverse(candidates[0])
        if len(candidates) == 1:
            return shared

        assigned = {
            drone_id: candidates[(drone_id - 1) % len(candidates)]
            for drone_id in range(1, self.map_data.drone_count + 1)
        }
        try:
            spread = Simulator(self.map_data, self.graph).traverse_routes(
                assigned
            )
        except ValueError:
            return shared

        return spread if len(spread) < len(shared) else shared
