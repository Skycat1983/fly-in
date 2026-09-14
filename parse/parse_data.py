"""Backward-compatible imports for the former single-file parser.

New code should import public parser types directly from ``parse``.  This
module remains so existing ``parse.parse_data`` imports do not break after the
implementation was divided into focused modules.
"""

from .errors import InputFormatError
from .models import (
    Connection,
    ConnectionMetadata,
    DroneCount,
    Hub,
    HubKind,
    HubMetadata,
    MapDefinition,
    Position,
    ZoneKind,
)
from .parser import InputParser
from .records import ParsedRecord, RecordFunction as RecordParser
from .syntax import parse_integer, parse_optional_integer, split_metadata

__all__ = [
    "Connection",
    "ConnectionMetadata",
    "DroneCount",
    "Hub",
    "HubKind",
    "HubMetadata",
    "InputFormatError",
    "InputParser",
    "MapDefinition",
    "ParsedRecord",
    "Position",
    "RecordParser",
    "ZoneKind",
    "parse_integer",
    "parse_optional_integer",
    "split_metadata",
]
