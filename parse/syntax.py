"""Low-level conversions for individual pieces of map-file syntax."""

from __future__ import annotations

from .errors import InputFormatError


def parse_integer(
    raw_value: str,
    *,
    line_number: int,
    field_name: str,
) -> int:
    """Convert a textual field to an integer.

    Args:
        raw_value: Text that should contain a base-10 integer.
        line_number: Source line used to identify an invalid value.
        field_name: Human-readable field name used in error messages.

    Returns:
        The integer represented by ``raw_value``.

    Raises:
        InputFormatError: If ``raw_value`` is not an integer.
    """

    try:
        return int(raw_value)
    except ValueError as error:
        raise InputFormatError(
            f"Line {line_number}: {field_name} must be an integer; "
            f"got {raw_value!r}"
        ) from error


def parse_optional_integer(
    values: dict[str, str],
    key: str,
    *,
    line_number: int,
) -> int | None:
    """Remove and convert an optional integer property.

    Args:
        values: Mutable metadata dictionary.  ``key`` is removed when it is
            present; all other entries remain unchanged.
        key: Metadata property to remove and convert.
        line_number: Source line used to identify an invalid value.

    Returns:
        The converted integer, or ``None`` when ``key`` is absent.

    Raises:
        InputFormatError: If the selected value is not an integer.
    """

    raw_value = values.pop(key, None)

    if raw_value is None:
        return None

    return parse_integer(
        raw_value,
        line_number=line_number,
        field_name=key,
    )


def split_metadata(
    text: str,
    *,
    line_number: int,
) -> tuple[str, dict[str, str]]:
    """Separate a record body from its optional bracketed metadata.

    For example, ``"alpha 4 1 [color=purple max_drones=3]"`` becomes
    ``("alpha 4 1", {"color": "purple", "max_drones": "3"})``.

    Args:
        text: Record body, optionally ending in ``[key=value ...]``.
        line_number: Source line used to identify malformed metadata.

    Returns:
        A pair containing the body before the metadata and a dictionary of
        unconverted metadata strings.  No metadata produces an empty dict.

    Raises:
        InputFormatError: If brackets are malformed, metadata is not at the
            end, a key is duplicated, or an entry is not ``key=value``.
    """

    text = text.strip()
    has_opening_bracket = "[" in text
    has_closing_bracket = "]" in text

    if not has_opening_bracket and not has_closing_bracket:
        return text, {}

    if not has_opening_bracket or not has_closing_bracket:
        raise InputFormatError(
            f"Line {line_number}: malformed metadata brackets in {text!r}"
        )

    opening_index = text.find("[")
    closing_index = text.rfind("]")

    if closing_index < opening_index:
        raise InputFormatError(
            f"Line {line_number}: malformed metadata brackets in {text!r}"
        )

    remaining_text = text[closing_index + 1:].strip()

    if remaining_text:
        raise InputFormatError(
            f"Line {line_number}: unexpected text after metadata: "
            f"{remaining_text!r}"
        )

    metadata_text = text[opening_index + 1: closing_index]

    if "[" in metadata_text or "]" in metadata_text:
        raise InputFormatError(
            f"Line {line_number}: nested metadata brackets are not supported"
        )

    main_text = text[:opening_index].strip()

    if not main_text:
        raise InputFormatError(
            f"Line {line_number}: missing data before metadata"
        )

    metadata: dict[str, str] = {}

    for item in metadata_text.split():
        key, separator, value = item.partition("=")

        if not separator or not key or not value:
            raise InputFormatError(
                f"Line {line_number}: expected metadata in "
                f"key=value form; got {item!r}"
            )

        if key in metadata:
            raise InputFormatError(
                f"Line {line_number}: duplicate metadata key {key!r}"
            )

        metadata[key] = value

    return main_text, metadata
