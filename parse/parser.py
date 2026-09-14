"""Orchestrate reading, parsing, assembling, and validating a map file."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from .errors import InputFormatError
from .models import (
    Connection,
    DroneCount,
    Hub,
    HubKind,
    MapDefinition,
)
from .records import RecordParser
from .validation import validate_map


class InputParser:
    """Parse one drone map file identified by a filesystem path."""

    def __init__(self, path: Path) -> None:
        """Store the map path without opening or parsing it.

        Args:
            path: File to open when ``parse`` is called.
        """

        self.path = path
        self._record_parser = RecordParser()

    def _read_lines(self) -> Iterator[tuple[int, str]]:
        """Yield meaningful source lines with their one-based line numbers.

        Returns:
            A lazy iterator of ``(line_number, cleaned_line)`` pairs.  Blank
            lines, full-line comments, and text after ``#`` are omitted.

        Raises:
            OSError: If the file cannot be opened or read.
            UnicodeError: If the file is not valid UTF-8.
        """

        with self.path.open("r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.partition("#")[0].strip()

                if line:
                    yield line_number, line

    def parse(self) -> MapDefinition:
        """Read the complete file and return its validated representation.

        Returns:
            A ``MapDefinition`` containing the drone count, start hub, regular
            hubs, end hub, and connections in their input order.

        Raises:
            OSError: If the input file cannot be opened or read.
            UnicodeError: If the input file is not valid UTF-8.
            InputFormatError: If any record or whole-map relationship violates
                the required format.

        Calling this method does not retain partial parse state, so the same
        parser instance may be called again after the file changes.
        """

        drone_count: DroneCount | None = None
        start_hub: Hub | None = None
        end_hub: Hub | None = None
        regular_hubs: list[Hub] = []
        connections: list[Connection] = []

        # Line numbers accompany records only until validation has produced
        # useful source-aware errors; they are not part of MapDefinition.
        located_hubs: list[tuple[int, Hub]] = []
        located_connections: list[tuple[int, Connection]] = []

        for record_index, (line_number, line) in enumerate(
            self._read_lines()
        ):
            record = self._record_parser.parse(line_number, line)

            if record_index == 0 and not isinstance(record, DroneCount):
                raise InputFormatError(
                    f"Line {line_number}: the first record must be nb_drones"
                )

            match record:
                case DroneCount():
                    if drone_count is not None:
                        raise InputFormatError(
                            f"Line {line_number}: duplicate nb_drones record"
                        )
                    drone_count = record

                case Hub(kind=HubKind.START):
                    if start_hub is not None:
                        raise InputFormatError(
                            f"Line {line_number}: duplicate start_hub record"
                        )
                    start_hub = record
                    located_hubs.append((line_number, record))

                case Hub(kind=HubKind.END):
                    if end_hub is not None:
                        raise InputFormatError(
                            f"Line {line_number}: duplicate end_hub record"
                        )
                    end_hub = record
                    located_hubs.append((line_number, record))

                case Hub(kind=HubKind.REGULAR):
                    regular_hubs.append(record)
                    located_hubs.append((line_number, record))

                case Connection():
                    connections.append(record)
                    located_connections.append((line_number, record))

        if drone_count is None:
            raise InputFormatError("Missing nb_drones record")

        if start_hub is None:
            raise InputFormatError("Missing start_hub record")

        if end_hub is None:
            raise InputFormatError("Missing end_hub record")

        result = MapDefinition(
            drone_count=drone_count.count,
            start_hub=start_hub,
            hubs=tuple(regular_hubs),
            end_hub=end_hub,
            connections=tuple(connections),
        )

        validate_map(
            result,
            located_hubs=located_hubs,
            located_connections=located_connections,
        )

        return result
