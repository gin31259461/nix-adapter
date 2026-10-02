"""Unit tests for nix_adapter.toml."""

from pathlib import Path
import tempfile
import unittest

from nix_adapter.toml import dump_toml, parse_toml, read_toml, write_toml


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

    def test_dump_toml_roundtrip(self):
        original = {
            "title": "TOML Example",
            "count": 10,
            "ratio": 3.14,
            "enabled": True,
            "items": ["apple", "banana"],
            "server": {"host": "127.0.0.1", "port": 8080},
            "clients": [{"id": 1, "name": "one"}, {"id": 2, "name": "two"}],
            "special.key": "dotted",
        }
        dumped = dump_toml(original)
        reloaded = parse_toml(dumped)
        self.assertEqual(reloaded, original)

    def test_write_toml_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "output.toml"
            data = {"app": {"name": "test", "active": True}}
            write_toml(path, data)
            reloaded = read_toml(path)
            self.assertEqual(reloaded, data)


if __name__ == "__main__":
    unittest.main()
