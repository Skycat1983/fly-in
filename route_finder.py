import heapq
from graph import Graph
from formatting import format_connection, format_hub  # noqa: F401
from parse import ZoneKind


"""
what are the edges here?
what are the node values?
what is the min priority queue? is that where we use heapq?
how do i read time complexity like this: O(V^2) or this O((V + E) log V)
and deduce meaning from it?

  Graph concept       Your project
  -----------------------------------------------
  node                Hub
  node identifier     hub.name
  edge                Connection
  edge weight         cost of entering destination
  best-known cost     self.distances[hub_name]
  parent in route     self.previous[hub_name]
  finished node       hub name in self.visited
"""


class RouteFinder:
    """Find least-cost routes through a parsed drone-zone graph."""

    def __init__(self, graph: Graph) -> None:
        """Store the graph and create empty search-state containers."""

        self.graph = graph
        self.distances: dict[str, int | float] = {}
        self.previous: dict[str, str | None] = {}
        self.visited: set[str] = set()

    def _initialize_search(self) -> list[tuple[int | float, str]]:
        """Reset the state needed at the beginning of Dijkstra's algorithm."""

        start_name = self.graph.map_data.start_hub.name

        self.distances = {
            name: float("inf")
            for name in self.graph.hubs_by_name
        }
        self.distances[start_name] = 0

        self.previous = {
            name: None
            for name in self.graph.hubs_by_name
        }
        self.visited = set()

        priority_queue: list[tuple[int | float, str]] = []
        heapq.heappush(priority_queue, (0, start_name))
        return priority_queue

    @staticmethod
    def _movement_cost(zone: ZoneKind) -> int | None:
        """Return the entry cost, or ``None`` when the zone is blocked."""

        if zone is ZoneKind.BLOCKED:
            return None
        if zone is ZoneKind.RESTRICTED:
            return 2
        return 1

    def find_shortest_path(
        self, *, excluded_connection: frozenset[str] | None = None,
    ) -> list[str]:
        """Return the least-cost route from the start hub to the end hub.

        An optional undirected connection can be excluded from this search.

        Returns:
            Hub names in travel order, including both endpoints. Returns an
            empty list when no route can reach the end hub.
        """

        priority_queue = self._initialize_search()
        start_name = self.graph.map_data.start_hub.name
        end_name = self.graph.map_data.end_hub.name

        while len(priority_queue) > 0:
            distance, name = heapq.heappop(priority_queue)
            # because the same name can be in the heap twice
            if name not in self.visited:
                self.visited.add(name)
                if name == end_name:
                    break

                for neighbour in self.graph.get_neighbours(name):
                    connection = frozenset((name, neighbour.name))
                    if connection == excluded_connection:
                        continue
                    step_cost = self._movement_cost(
                        neighbour.metadata.zone
                    )
                    if step_cost is None:
                        continue

                    new_distance = distance + step_cost
                    existing = self.distances[neighbour.name]
                    # if best distance so far
                    if new_distance < existing:
                        self.distances[neighbour.name] = new_distance
                        self.previous[neighbour.name] = name
                        heapq.heappush(priority_queue,
                                       (new_distance, neighbour.name))
        if self.distances[end_name] == float("inf"):
            return []

        route: list[str] = []
        current = end_name
        while current != start_name:
            route.append(current)
            predecessor = self.previous[current]
            if predecessor is None:
                return []
            current = predecessor

        route.append(start_name)
        route.reverse()
        # TODO: add exceptions for failure details.
        return route

    def find_candidate_paths(self, max_paths: int = 3) -> list[list[str]]:
        """Find the best route and alternatives avoiding one of its links.

        This bounded search does not enumerate every possible route. Each
        alternative comes from a new Dijkstra search with one connection of
        the best route excluded.
        """

        if max_paths < 1:
            raise ValueError("max_paths must be positive")

        best = self.find_shortest_path()
        if not best or max_paths == 1:
            return [best] if best else []

        end_name = self.graph.map_data.end_hub.name
        alternatives: dict[tuple[str, ...], int | float] = {}
        for first, second in zip(best, best[1:]):
            finder = RouteFinder(self.graph)
            excluded = frozenset((first, second))
            route = finder.find_shortest_path(
                excluded_connection=excluded
            )
            if route and route != best:
                alternatives[tuple(route)] = finder.distances[end_name]

        ordered = sorted(
            alternatives,
            key=lambda route: (alternatives[route], route),
        )
        return [best, *[list(route) for route in ordered[:max_paths - 1]]]
