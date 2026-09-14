"""Public interface for parsing drone map files.

Callers normally need ``InputParser`` and, when reporting bad input,
``InputFormatError``.  The remaining exports describe the resulting map.
"""

from .errors import InputFormatError
from .models import (
    Connection,
    ConnectionMetadata,
    Hub,
    HubKind,
    HubMetadata,
    MapDefinition,
    Position,
    ZoneKind,
)
from .parser import InputParser

__all__ = [
    "Connection",
    "ConnectionMetadata",
    "Hub",
    "HubKind",
    "HubMetadata",
    "InputFormatError",
    "InputParser",
    "MapDefinition",
    "Position",
    "ZoneKind",
]
