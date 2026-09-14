"""Regression tests for the public drone-map parser interface."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from parse import InputFormatError, InputParser, MapDefinition, ZoneKind
from parse.syntax import parse_optional_integer, split_metadata


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = PROJECT_ROOT / "maps"


class InputParserTests(unittest.TestCase):
    """Exercise complete files through the public ``InputParser`` API."""

    def parse_text(self, text: str) -> MapDefinition:
        """Write ``text`` to a temporary map and return its parsed result."""

        with TemporaryDirectory() as directory:
            path = Path(directory) / "map.txt"
            path.write_text(text, encoding="utf-8")
            return InputParser(path).parse()

    def test_every_bundled_map_parses(self) -> None:
        """All example maps should remain valid after internal refactors."""

        paths = sorted(MAP_ROOT.rglob("*.txt"))
        self.assertEqual(len(paths), 10)

        for path in paths:
            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                result = InputParser(path).parse()
                self.assertGreater(result.drone_count, 0)
                self.assertTrue(result.start_hub.name)
                self.assertTrue(result.end_hub.name)

    def test_parses_typed_metadata_and_preserves_unknown_fields(self) -> None:
        """Known metadata is typed while extensions remain available."""

        result = self.parse_text(
            """\
nb_drones: 2
start_hub: start 0 0 [max_drones=99]
hub: middle 1 0 [zone=priority max_drones=3 note=charging]
end_hub: end 2 0
connection: start-middle [max_link_capacity=2 surface=air]
connection: middle-end
"""
        )

        middle = result.hubs[0]
        self.assertEqual(result.drone_count, 2)
        self.assertEqual(result.start_hub.metadata.max_drones, None)
        self.assertEqual(middle.metadata.zone, ZoneKind.PRIORITY)
        self.assertEqual(middle.metadata.max_drones, 3)
        self.assertEqual(middle.metadata.extra, {"note": "charging"})
        self.assertEqual(
            result.connections[0].metadata.max_link_capacity,
            2,
        )
        self.assertEqual(
            result.connections[0].metadata.extra,
            {"surface": "air"},
        )

    def test_rejects_duplicate_hub_names_with_source_lines(self) -> None:
        """Whole-map validation should retain useful line information."""

        with self.assertRaisesRegex(
            InputFormatError,
            r"Line 3: duplicate hub name 'same'; first defined on line 2",
        ):
            self.parse_text(
                """\
nb_drones: 1
start_hub: same 0 0
end_hub: same 1 0
"""
            )


class SyntaxTests(unittest.TestCase):
    """Specify the input, output, and mutation of syntax helpers."""

    def test_split_metadata_returns_body_and_untyped_values(self) -> None:
        """Bracket contents become strings for record-level conversion."""

        body, metadata = split_metadata(
            "alpha 4 1 [color=purple max_drones=3]",
            line_number=7,
        )

        self.assertEqual(body, "alpha 4 1")
        self.assertEqual(
            metadata,
            {"color": "purple", "max_drones": "3"},
        )

    def test_parse_optional_integer_removes_only_selected_key(self) -> None:
        """The helper's documented mutation remains intentional and narrow."""

        values = {"max_drones": "3", "color": "purple"}

        result = parse_optional_integer(
            values,
            "max_drones",
            line_number=7,
        )

        self.assertEqual(result, 3)
        self.assertEqual(values, {"color": "purple"})


if __name__ == "__main__":
    unittest.main()
