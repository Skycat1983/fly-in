"""Typed values produced by the drone map parser.

The parser converts text records into these immutable domain objects.  Code
that consumes a parsed map should depend on these types rather than on the
input file's textual representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class HubKind(str, Enum):
    """Identify whether a hub is the start, a regular hub, or the end."""

    START = "start_hub"
    REGULAR = "hub"
    END = "end_hub"


class ZoneKind(str, Enum):
    """Describe the movement rule attached to a hub's zone."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass(frozen=True)
class DroneCount:
    """Intermediate record containing the number of drones in the map."""

    count: int


@dataclass(frozen=True)
class Position:
    """Integer coordinates read from a hub record."""

    x: int
    y: int


@dataclass(frozen=True)
class HubMetadata:
    """Typed metadata attached to a hub.

    Attributes:
        color: Optional display color from the input.
        zone: Movement behavior for the hub; defaults to a normal zone.
        max_drones: Hub capacity.  Start and end hubs use ``None`` to mean
            unlimited capacity.
        extra: Unrecognized metadata retained as unconverted strings.
    """

    color: str | None = None
    zone: ZoneKind = ZoneKind.NORMAL
    max_drones: int | None = 1
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectionMetadata:
    """Typed metadata attached to a connection.

    Attributes:
        max_link_capacity: Number of drones that may use the connection at
            once.  The input default is one.
        extra: Unrecognized metadata retained as unconverted strings.
    """

    max_link_capacity: int = 1
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Hub:
    """A named map location produced from one hub record."""

    kind: HubKind
    name: str
    position: Position
    metadata: HubMetadata = field(default_factory=HubMetadata)


@dataclass(frozen=True)
class Connection:
    """An undirected link between two hubs named by its endpoints."""

    source: str
    destination: str
    metadata: ConnectionMetadata = field(
        default_factory=ConnectionMetadata
    )


@dataclass(frozen=True)
class MapDefinition:
    """Complete, validated representation of one drone map file.

    ``hubs`` contains only regular hubs.  Use ``all_hubs`` when the start and
    end hubs should be included as well.
    """

    drone_count: int
    start_hub: Hub
    hubs: tuple[Hub, ...]
    end_hub: Hub
    connections: tuple[Connection, ...]

    @property
    def all_hubs(self) -> tuple[Hub, ...]:
        """Return the start, regular, and end hubs in input order."""

        return (self.start_hub, *self.hubs, self.end_hub)
