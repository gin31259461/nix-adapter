"""Unit tests for nix_adapter.toml."""

from pathlib import Path
import tempfile
import unittest

from nix_adapter.toml import parse_toml, read_toml


class TomlTests(unittest.TestCase):
    def test_parse_toml_string_and_bytes(self):
        doc = 'key = "value"\nnumber = 42\n[section]\nenabled = true\n'
        parsed = parse_toml(doc)
        self.assertEqual(parsed["key"], "value")
        self.assertEqual(parsed["number"], 42)
        self.assertEqual(parsed["section"]["enabled"], True)

        parsed_bytes = parse_toml(doc.encode("utf-8"))
        self.assertEqual(parsed_bytes, parsed)

    def test_read_toml_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text('title = "test"\n')
            res = read_toml(path)
            self.assertEqual(res, {"title": "test"})


if __name__ == "__main__":
    unittest.main()
