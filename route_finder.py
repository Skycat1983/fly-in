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

    def solve(self):
        priority_queue = self._initialize_search()

        while len(priority_queue) > 0:
            distance, name = heapq.heappop(priority_queue)
            print()
            adjacent = []
            for neighbour in self.graph.get_neighbours(name):
                # from here where coul i go next
                connection = self.graph.get_connection(name, neighbour.name)
                zone = neighbour.metadata.zone
                print(zone)
                step_cost  = 0
                if zone in (ZoneKind.PRIORITY, ZoneKind.NORMAL):
                    step_cost = 1
                if zone == ZoneKind.RESTRICTED:
                    step_cost = 2
                new_distance = distance + step_cost
                # if kind == "BLOCKED":
                #     pass
                # cost = 1
                # new_distance = distance + cost
                # print(kind)
                # print(connection.metadata.)
                # if i went there from here what would the distance be.



        # current_name = self.graph.get_hub("start").name
        # neighbours = self.graph.get_neighbours(current_name)
        # for neighbour in neighbours:
        #     adjacent = neighbour.name
        #     connection = self.graph.get_connection(current_name, adjacent)
        #     print(format_connection(connection))

        # print(start)
    pass
