"""Tests for recursive and domain-specific display formatting."""

import unittest

from formatting import format_hub, format_value
from parse import Hub, HubKind, HubMetadata, Position, ZoneKind


class FormattingTests(unittest.TestCase):
    """Verify formatting of domain objects and nested containers."""

    def test_formats_hub_with_domain_specific_meaning(self) -> None:
        """A missing start capacity is displayed as unlimited."""

        hub = Hub(
            kind=HubKind.START,
            name="launch",
            position=Position(2, 3),
            metadata=HubMetadata(
                zone=ZoneKind.PRIORITY,
                max_drones=None,
            ),
        )

        self.assertEqual(
            format_hub(hub),
            "launch: position=(2, 3), type=start_hub, "
            "zone=priority, capacity=unlimited",
        )

    def test_formats_nested_containers_without_mutating_them(self) -> None:
        """Container handlers recursively format their child values."""

        value = {"route": ["start", ("middle", "end")]}

        self.assertEqual(
            format_value(value),
            "{\n"
            "  route: [\n"
            "    start,\n"
            "    (\n"
            "      middle,\n"
            "      end\n"
            "    )\n"
            "  ]\n"
            "}",
        )
        self.assertEqual(
            value,
            {"route": ["start", ("middle", "end")]},
        )


if __name__ == "__main__":
    unittest.main()
