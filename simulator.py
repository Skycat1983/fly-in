"""Drone state and simultaneous movement scheduling."""

from __future__ import annotations

from dataclasses import dataclass

from formatting import format_movement
from graph import Graph, MapDefinition
from parse import Connection, Hub, ZoneKind


@dataclass(frozen=True)
class MoveProposal:
    """Describe one possible move without changing drone state."""

    drone: Drone
    destination: Hub | Connection
    connection: Connection
    next_route_index: int
    in_transit_to: Hub | None
    required: bool = False

    @property
    def output_name(self) -> str:
        """Return the hub or connection name printed for this move."""

        if isinstance(self.destination, Hub):
            return self.destination.name
        return f"{self.destination.source}-{self.destination.destination}"


class Drone:
    """Track one drone's position along a planned route."""

    def __init__(self, graph: Graph, drone_id: int) -> None:
        """Place a numbered drone at the map's start hub."""

        self.graph = graph
        self.drone_id: int = drone_id
        self.location: Hub | Connection = graph.map_data.start_hub
        self.route_index: int = 0
        self.in_transit_to: Hub | None = None

    def get_id(self) -> int:
        """Return this drone's identifier."""

        return self.drone_id

    def propose_move(self, path: list[str]) -> MoveProposal | None:
        """Describe the next move, or None after delivery."""

        if not path:
            raise ValueError("A drone cannot move without a route")

        if self.in_transit_to is not None:
            if not isinstance(self.location, Connection):
                raise ValueError("A drone in transit must occupy a connection")
            return MoveProposal(
                self, self.in_transit_to, self.location,
                self.route_index + 1, None, required=True,
            )

        if self.route_index == len(path) - 1:
            return None

        next_index = self.route_index + 1
        destination = self.graph.get_hub(path[next_index])
        connection = self.graph.get_connection(
            path[self.route_index], destination.name
        )
        if destination.metadata.zone is ZoneKind.RESTRICTED:
            # ? get clarity here
            return MoveProposal(
                self, connection, connection,
                self.route_index, destination,
            )

        return MoveProposal(
            self, destination, connection, next_index, None,
        )

    def apply_move(self, move: MoveProposal) -> None:
        """Apply a move that the simulator has accepted for this turn."""

        self.location = move.destination
        self.route_index = move.next_route_index
        self.in_transit_to = move.in_transit_to

    def move_one_turn(self, path: list[str]) -> str | None:
        """Advance this drone alone by one turn, returning its new location."""

        move = self.propose_move(path)
        if move is None:
            return None
        self.apply_move(move)
        return move.output_name


class Simulator:
    """Advance drones through routes one turn at a time."""

    def __init__(self,
                 map_data: MapDefinition,
                 graph: Graph) -> None:
        """Keep the map, graph, and count of completed turns."""

        self.map_data = map_data
        self.graph = graph
        self.turn_counter = 0

    def _choose_moves(
        self, proposals: list[MoveProposal], drones: list[Drone],
    ) -> list[MoveProposal]:
        """Accept moves that fit hub, reservation, and connection capacity."""

        # Start with the positions and promised arrivals at this turn's start.
        occupancy = {name: 0 for name in self.graph.hubs_by_name}
        reserved = {name: 0 for name in self.graph.hubs_by_name}
        for drone in drones:
            if isinstance(drone.location, Hub):
                occupancy[drone.location.name] += 1
            if drone.in_transit_to is not None:
                reserved[drone.in_transit_to.name] += 1

        used_links: dict[tuple[str, str], int] = {}
        accepted: list[MoveProposal] = []
        # Required arrivals go first; leaders then make room for followers.
        order = sorted(
            proposals,
            key=lambda move: (
                not move.required,
                -move.drone.route_index,
                move.drone.drone_id,
            ),
        )

        for move in order:
            link = (move.connection.source, move.connection.destination)
            link_capacity = move.connection.metadata.max_link_capacity
            if used_links.get(link, 0) >= link_capacity:
                if move.required:
                    raise ValueError(
                        "A required arrival exceeds link capacity"
                    )
                continue

            target_hub = move.in_transit_to
            if isinstance(move.destination, Hub):
                target_hub = move.destination
            if target_hub is None:
                raise ValueError("A move must target a hub or its connection")

            capacity = target_hub.metadata.max_drones
            planned_occupancy = (
                occupancy[target_hub.name] + reserved[target_hub.name]
            )
            if capacity is not None:
                # Arrival replaces its reservation; a new move needs a slot.
                if move.required and planned_occupancy > capacity:
                    raise ValueError("A required arrival exceeds hub capacity")
                if not move.required and planned_occupancy >= capacity:
                    continue

            source = move.drone.location
            # Change projected counts only after the move has passed checks.
            if isinstance(source, Hub):
                occupancy[source.name] -= 1
            if move.required:
                reserved[target_hub.name] -= 1
                occupancy[target_hub.name] += 1
            elif isinstance(move.destination, Connection):
                reserved[target_hub.name] += 1
            else:
                occupancy[target_hub.name] += 1

            used_links[link] = used_links.get(link, 0) + 1
            accepted.append(move)

        return accepted

    def traverse(self, path: list[str]) -> list[str]:
        """Assign one route to every drone and schedule their turns."""

        if not path:
            raise ValueError("No route reaches the end hub")

        routes_by_drone = {
            drone_id: path
            for drone_id in range(1, self.map_data.drone_count + 1)
        }
        return self.traverse_routes(routes_by_drone)

    def traverse_routes(
        self, routes_by_drone: dict[int, list[str]],
    ) -> list[str]:
        """Schedule drones using their assigned routes, one line per turn."""

        expected_ids = set(range(1, self.map_data.drone_count + 1))
        if set(routes_by_drone) != expected_ids:
            raise ValueError("Each drone needs exactly one assigned route")

        start_name = self.map_data.start_hub.name
        end_name = self.map_data.end_hub.name
        for route in routes_by_drone.values():
            if not route or route[0] != start_name or route[-1] != end_name:
                raise ValueError("Each route must run from start to end")
            for source, destination in zip(route, route[1:]):
                try:
                    self.graph.get_connection(source, destination)
                    hub = self.graph.get_hub(destination)
                except KeyError as error:
                    raise ValueError(
                        "A route contains an invalid step"
                    ) from error
                if hub.metadata.zone is ZoneKind.BLOCKED:
                    raise ValueError("A route cannot enter a blocked hub")

        drones = [
            Drone(self.graph, drone_id)
            for drone_id in range(1, self.map_data.drone_count + 1)
        ]
        self.turn_counter = 0
        turn_lines: list[str] = []
        while True:
            # 1. Propose moves from the same turn-start state.
            proposals = [
                move for drone in drones
                if (
                    move := drone.propose_move(
                        routes_by_drone[drone.drone_id]
                    )
                ) is not None
            ]
            if not proposals:
                break

            # 2. Check capacity, including space reserved for transit arrival.
            accepted = self._choose_moves(proposals, drones)
            if not accepted:
                raise ValueError("No drone can move; the schedule is stuck")

            # 3. Apply all accepted moves after the whole turn is decided.
            for move in accepted:
                move.drone.apply_move(move)

            # 4. Record one line with only the drones that moved.
            self.turn_counter += 1
            by_drone_id = sorted(
                accepted, key=lambda item: item.drone.drone_id
            )
            turn_lines.append(" ".join(
                format_movement(move.drone.get_id(), move.output_name)
                for move in by_drone_id
            ))

        return turn_lines
