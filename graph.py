"""Graph indexes and lookup operations for parsed drone maps."""

from typing import TypeAlias

from parse import Connection, Hub, MapDefinition


HubsByName: TypeAlias = dict[str, Hub]
ConnectionsByNeighbor: TypeAlias = dict[str, Connection]
AdjacencyByName: TypeAlias = dict[str, ConnectionsByNeighbor]


class Graph:
    """Provide efficient hub, neighbor, and connection lookups for a map."""

    map_data: MapDefinition
    hubs_by_name: HubsByName
    adjacency_by_name: AdjacencyByName

    def __init__(self, map_data: MapDefinition) -> None:
        """Build graph indexes from a parsed map definition."""

        self.map_data = map_data
        self.hubs_by_name = {
            hub.name: hub
            for hub in map_data.all_hubs
        }
        self.adjacency_by_name = {
            hub_name: {}
            for hub_name in self.hubs_by_name
        }

        for connection in map_data.connections:
            self.adjacency_by_name[connection.source][
                connection.destination
            ] = connection
            self.adjacency_by_name[connection.destination][
                connection.source
            ] = connection

    def get_hub(self, name: str) -> Hub:
        """Return the hub named by ``name``."""

        return self.hubs_by_name[name]

    def get_neighbours(self, name: str) -> list[Hub]:
        """Return every hub directly connected to the named hub."""

        return [
            self.hubs_by_name[neighbor_name]
            for neighbor_name in self.adjacency_by_name[name]
        ]

    def get_connection(self, first: str, second: str) -> Connection:
        """Return the connection joining two directly connected hubs."""

        return self.adjacency_by_name[first][second]
