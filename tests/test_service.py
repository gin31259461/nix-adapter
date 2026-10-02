"""Unit tests for BaseServiceAdapter."""

from pathlib import Path
import tempfile
import unittest

from nix_adapter.exceptions import Conflict
from nix_adapter.service import BaseServiceAdapter


class ServiceAdapterTests(unittest.TestCase):
    def test_path_validation(self):
        adapter = BaseServiceAdapter(desired={"valid": "/etc/foo", "traversal": "/etc/../bar", "relative": "relative"})
        self.assertEqual(adapter.path("valid"), Path("/etc/foo"))
        with self.assertRaises(Conflict):
            adapter.path("traversal")
        with self.assertRaises(Conflict):
            adapter.path("relative")

    def test_validate_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "config.toml"
            file_path.write_text("ok")
            file_path.chmod(0o644)

            adapter = BaseServiceAdapter(desired={"config": "/config.toml"}, root=root)
            validated = adapter.validate_file("config")
            self.assertEqual(validated, file_path)

            # Invalid permissions (world writable)
            file_path.chmod(0o666)
            with self.assertRaises(Conflict):
                adapter.validate_file("config")


if __name__ == "__main__":
    unittest.main()
