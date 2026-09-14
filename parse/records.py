"""Convert individual map-file lines into typed records.

This module handles the syntax and metadata of one record at a time.  It does
not enforce rules that require knowledge of other records; those belong in
``validation.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

from .errors import InputFormatError
from .models import (
    Connection,
    ConnectionMetadata,
    DroneCount,
    Hub,
    HubKind,
    HubMetadata,
    Position,
    ZoneKind,
)
from .syntax import parse_integer, parse_optional_integer, split_metadata

ParsedRecord: TypeAlias = DroneCount | Hub | Connection
RecordFunction: TypeAlias = Callable[[int, str], ParsedRecord]


class RecordParser:
    """Parse one cleaned map-file line into a typed record."""

    def __init__(self) -> None:
        """Create the record-type dispatch table used by ``parse``."""

        self._record_parsers: dict[str, RecordFunction] = {
            "nb_drones": self._parse_drone_count,
            "start_hub": self._parse_start_hub,
            "hub": self._parse_regular_hub,
            "end_hub": self._parse_end_hub,
            "connection": self._parse_connection,
        }

    def parse(self, line_number: int, line: str) -> ParsedRecord:
        """Identify a line's record type and parse its body.

        Args:
            line_number: One-based source line used in error messages.
            line: Cleaned, nonempty input in ``record_type: body`` form.

        Returns:
            A ``DroneCount``, ``Hub``, or ``Connection`` record.

        Raises:
            InputFormatError: If the record type, separator, body, or record
                contents do not follow the required format.
        """

        record_type, separator, body = line.partition(":")

        if not separator:
            raise InputFormatError(
                f"Line {line_number}: expected ':' in {line!r}"
            )

        record_type = record_type.strip()
        body = body.strip()

        if not record_type:
            raise InputFormatError(
                f"Line {line_number}: missing record type in {line!r}"
            )

        if not body:
            raise InputFormatError(
                f"Line {line_number}: missing data after ':' in {line!r}"
            )

        parser = self._record_parsers.get(record_type)

        if parser is None:
            raise InputFormatError(
                f"Line {line_number}: unknown record type {record_type!r}"
            )

        return parser(line_number, body)

    def _parse_drone_count(
        self,
        line_number: int,
        body: str,
    ) -> DroneCount:
        """Convert an ``nb_drones`` body into a ``DroneCount`` record."""

        parts = body.split()

        if len(parts) != 1:
            raise InputFormatError(
                f"Line {line_number}: nb_drones expects exactly "
                f"one integer; got {body!r}"
            )

        count = parse_integer(
            parts[0],
            line_number=line_number,
            field_name="nb_drones",
        )

        return DroneCount(count=count)

    def _parse_start_hub(self, line_number: int, body: str) -> Hub:
        """Convert a ``start_hub`` body into a start ``Hub``."""

        return self._parse_hub(line_number, body, kind=HubKind.START)

    def _parse_regular_hub(self, line_number: int, body: str) -> Hub:
        """Convert a ``hub`` body into a regular ``Hub``."""

        return self._parse_hub(line_number, body, kind=HubKind.REGULAR)

    def _parse_end_hub(self, line_number: int, body: str) -> Hub:
        """Convert an ``end_hub`` body into an end ``Hub``."""

        return self._parse_hub(line_number, body, kind=HubKind.END)

    def _parse_hub(
        self,
        line_number: int,
        body: str,
        *,
        kind: HubKind,
    ) -> Hub:
        """Convert ``name x y [metadata]`` into a ``Hub``.

        Args:
            line_number: One-based source line used in error messages.
            body: Text after the record's colon.
            kind: Hub role supplied by the record-type dispatcher.

        Returns:
            A hub with typed coordinates and metadata.

        Raises:
            InputFormatError: If the name, coordinates, or metadata are
                malformed.
        """

        main_text, raw_metadata = split_metadata(
            body,
            line_number=line_number,
        )
        parts = main_text.split()

        if len(parts) != 3:
            raise InputFormatError(
                f"Line {line_number}: {kind.value} expects "
                f"'name x y'; got {main_text!r}"
            )

        name, raw_x, raw_y = parts

        # A dash separates connection endpoints, so accepting one in a hub
        # name would make connection records ambiguous.
        if "-" in name:
            raise InputFormatError(
                f"Line {line_number}: hub names cannot contain '-'; "
                f"got {name!r}"
            )

        position = Position(
            x=parse_integer(
                raw_x,
                line_number=line_number,
                field_name="x coordinate",
            ),
            y=parse_integer(
                raw_y,
                line_number=line_number,
                field_name="y coordinate",
            ),
        )
        metadata = self._parse_hub_metadata(
            line_number,
            raw_metadata,
            kind=kind,
        )

        return Hub(
            kind=kind,
            name=name,
            position=position,
            metadata=metadata,
        )

    def _parse_hub_metadata(
        self,
        line_number: int,
        raw_metadata: dict[str, str],
        *,
        kind: HubKind,
    ) -> HubMetadata:
        """Convert untyped hub metadata into ``HubMetadata``.

        Args:
            line_number: One-based source line used in error messages.
            raw_metadata: Metadata strings produced by ``split_metadata``.
                The supplied dictionary is not modified.
            kind: Hub role, used to choose the capacity default.

        Returns:
            Typed known fields plus unknown fields in ``extra``.  Regular hubs
            default to capacity one; start and end hubs use unlimited capacity
            and ignore any supplied ``max_drones`` value.

        Raises:
            InputFormatError: If ``zone`` or ``max_drones`` is invalid.
        """

        values = dict(raw_metadata)
        color = values.pop("color", None)
        raw_zone = values.pop("zone", ZoneKind.NORMAL.value)

        try:
            zone = ZoneKind(raw_zone)
        except ValueError as error:
            valid_zones = ", ".join(zone.value for zone in ZoneKind)
            raise InputFormatError(
                f"Line {line_number}: zone must be one of "
                f"{valid_zones}; got {raw_zone!r}"
            ) from error

        if kind is HubKind.REGULAR:
            max_drones = parse_optional_integer(
                values,
                "max_drones",
                line_number=line_number,
            )
            if max_drones is None:
                max_drones = 1
        else:
            values.pop("max_drones", None)
            max_drones = None

        return HubMetadata(
            color=color,
            zone=zone,
            max_drones=max_drones,
            extra=values,
        )

    def _parse_connection(
        self,
        line_number: int,
        body: str,
    ) -> Connection:
        """Convert ``source-destination [metadata]`` into a connection.

        Args:
            line_number: One-based source line used in error messages.
            body: Text after the connection record's colon.

        Returns:
            A connection with endpoint names and typed metadata.

        Raises:
            InputFormatError: If endpoints or metadata are malformed.
        """

        main_text, raw_metadata = split_metadata(
            body,
            line_number=line_number,
        )
        endpoints = main_text.split("-")

        if len(endpoints) != 2:
            raise InputFormatError(
                f"Line {line_number}: connection expects "
                f"'source-destination'; got {main_text!r}"
            )

        source, destination = (
            endpoint.strip() for endpoint in endpoints
        )

        if not source or not destination:
            raise InputFormatError(
                f"Line {line_number}: connection endpoints cannot be empty"
            )

        metadata = self._parse_connection_metadata(
            line_number,
            raw_metadata,
        )

        return Connection(
            source=source,
            destination=destination,
            metadata=metadata,
        )

    def _parse_connection_metadata(
        self,
        line_number: int,
        raw_metadata: dict[str, str],
    ) -> ConnectionMetadata:
        """Convert untyped connection metadata into typed metadata.

        Args:
            line_number: One-based source line used in error messages.
            raw_metadata: Metadata strings produced by ``split_metadata``.
                The supplied dictionary is not modified.

        Returns:
            Typed capacity, defaulting to one, plus unknown fields in
            ``extra``.

        Raises:
            InputFormatError: If ``max_link_capacity`` is not an integer.
        """

        values = dict(raw_metadata)
        max_link_capacity = parse_optional_integer(
            values,
            "max_link_capacity",
            line_number=line_number,
        )

        if max_link_capacity is None:
            max_link_capacity = 1

        return ConnectionMetadata(
            max_link_capacity=max_link_capacity,
            extra=values,
        )
