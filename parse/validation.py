"""Validate rules that depend on more than one parsed map record."""

from __future__ import annotations

from collections.abc import Sequence

from .errors import InputFormatError
from .models import Connection, Hub, HubKind, MapDefinition

LocatedHub = tuple[int, Hub]
LocatedConnection = tuple[int, Connection]


def validate_map(
    map_data: MapDefinition,
    *,
    located_hubs: Sequence[LocatedHub],
    located_connections: Sequence[LocatedConnection],
) -> None:
    """Validate relationships and positive capacities across a complete map.

    Args:
        map_data: Fully assembled map whose record relationships must be
            checked.
        located_hubs: ``(line_number, hub)`` pairs for every parsed hub.
        located_connections: ``(line_number, connection)`` pairs for every
            parsed connection.

    Returns:
        ``None`` when every whole-map rule is satisfied.

    Raises:
        InputFormatError: If counts or capacities are non-positive, names or
            connections are duplicated, an endpoint is unknown, or a
            connection appears before one of its endpoints.

    The supplied map and sequences are read but never modified.
    """

    if map_data.drone_count <= 0:
        raise InputFormatError("nb_drones must be greater than zero")

    hub_lines_by_name: dict[str, int] = {}

    for line_number, hub in located_hubs:
        previous_line = hub_lines_by_name.get(hub.name)

        if previous_line is not None:
            raise InputFormatError(
                f"Line {line_number}: duplicate hub name {hub.name!r}; "
                f"first defined on line {previous_line}"
            )

        hub_lines_by_name[hub.name] = line_number
        max_drones = hub.metadata.max_drones

        if (
            hub.kind is HubKind.REGULAR
            and max_drones is not None
            and max_drones <= 0
        ):
            raise InputFormatError(
                f"Line {line_number}: max_drones must be greater than zero"
            )

    known_hub_names = set(hub_lines_by_name)
    connection_lines_by_endpoints: dict[frozenset[str], int] = {}

    for line_number, connection in located_connections:
        if connection.source not in known_hub_names:
            raise InputFormatError(
                f"Line {line_number}: unknown connection "
                f"source {connection.source!r}"
            )

        if connection.destination not in known_hub_names:
            raise InputFormatError(
                f"Line {line_number}: unknown connection "
                f"destination {connection.destination!r}"
            )

        source_line = hub_lines_by_name[connection.source]
        destination_line = hub_lines_by_name[connection.destination]

        if source_line > line_number:
            raise InputFormatError(
                f"Line {line_number}: connection source "
                f"{connection.source!r} must be defined before "
                f"the connection"
            )

        if destination_line > line_number:
            raise InputFormatError(
                f"Line {line_number}: connection destination "
                f"{connection.destination!r} must be defined before "
                f"the connection"
            )

        endpoints = frozenset(
            (connection.source, connection.destination)
        )
        previous_line = connection_lines_by_endpoints.get(endpoints)

        if previous_line is not None:
            raise InputFormatError(
                f"Line {line_number}: duplicate connection "
                f"{connection.source!r}-{connection.destination!r}; "
                f"first defined on line {previous_line}"
            )

        connection_lines_by_endpoints[endpoints] = line_number
        capacity = connection.metadata.max_link_capacity

        if capacity <= 0:
            raise InputFormatError(
                f"Line {line_number}: max_link_capacity must be "
                f"greater than zero"
            )
