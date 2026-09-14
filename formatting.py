"""Human-readable formatting for parsed map data and nested containers."""

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from functools import singledispatch

from parse import Connection, Hub


@singledispatch
def format_value(value: object, indent: int = 0) -> str:
    """Return a human-readable representation of ``value``.

    Scalar values use their normal string representation. Dataclasses and
    registered container types are formatted recursively.
    """

    if isinstance(value, Enum):
        return format_value(value.value, indent)

    if is_dataclass(value) and not isinstance(value, type):
        contents = {
            field.name: getattr(value, field.name)
            for field in fields(value)
        }
        return f"{type(value).__name__} {format_value(contents, indent)}"

    return str(value)


@format_value.register(Mapping)
def format_mapping(
    value: Mapping[object, object],
    indent: int = 0,
) -> str:
    """Format mappings recursively, preserving their iteration order."""

    if not value:
        return "{}"

    inner_indent = indent + 1
    padding = "  " * inner_indent
    closing_padding = "  " * indent
    contents = ",\n".join(
        f"{padding}{format_value(key, inner_indent)}: "
        f"{format_value(item, inner_indent)}"
        for key, item in value.items()
    )

    return f"{{\n{contents}\n{closing_padding}}}"


@format_value.register(list)
@format_value.register(tuple)
def format_sequence(
    value: list[object] | tuple[object, ...],
    indent: int = 0,
) -> str:
    """Format lists and tuples recursively without modifying them."""

    opening, closing = (
        ("[", "]") if isinstance(value, list) else ("(", ")")
    )

    if not value:
        return opening + closing

    inner_indent = indent + 1
    padding = "  " * inner_indent
    closing_padding = "  " * indent
    contents = ",\n".join(
        f"{padding}{format_value(item, inner_indent)}"
        for item in value
    )

    return f"{opening}\n{contents}\n{closing_padding}{closing}"


@format_value.register
def format_hub(hub: Hub, indent: int = 0) -> str:
    """Return one hub as a concise, human-readable CLI line."""

    capacity = hub.metadata.max_drones
    capacity_text = "unlimited" if capacity is None else str(capacity)

    return (
        f"{hub.name}: "
        f"position=({hub.position.x}, {hub.position.y}), "
        f"type={hub.kind.value}, "
        f"zone={hub.metadata.zone.value}, "
        f"capacity={capacity_text}"
    )


@format_value.register
def format_connection(connection: Connection, indent: int = 0) -> str:
    """Return one connection as a concise, human-readable CLI line."""

    return (
        f"{connection.source} <-> {connection.destination} "
        f"(capacity={connection.metadata.max_link_capacity})"
    )
