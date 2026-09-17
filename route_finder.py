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
    def __init__(self, graph: Graph) -> None:
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

    def solve(self) -> list[str]:
        priority_queue = self._initialize_search()
        start_name = self.graph.map_data.start_hub.name
        end_name = self.graph.map_data.end_hub.name

        while len(priority_queue) > 0:
            distance, name = heapq.heappop(priority_queue)
            if name not in self.visited:
                self.visited.add(name)
                if name == end_name:
                    break

                for neighbour in self.graph.get_neighbours(name):
                    zone = neighbour.metadata.zone
                    if zone != ZoneKind.BLOCKED:
                        step_cost = 0
                        if zone in (ZoneKind.PRIORITY, ZoneKind.NORMAL):
                            step_cost = 1
                        if zone == ZoneKind.RESTRICTED:
                            step_cost = 2
                        new_distance = distance + step_cost
                        existing = self.distances[neighbour.name]
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
        return route
