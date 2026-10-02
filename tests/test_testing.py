"""Unit tests for nix_adapter.testing."""

import subprocess
import unittest

from nix_adapter.testing import FakeNative, FakeProcess


class TestingTests(unittest.TestCase):
    def test_fake_native_available(self):
        fake = FakeNative(available_commands=["curl", "systemctl"])
        self.assertTrue(fake.available("curl"))
        self.assertTrue(fake.available("systemctl"))
        self.assertFalse(fake.available("missing"))

    def test_fake_native_run_recording(self):
        fake = FakeNative(
            responses={
                ("echo", "hi"): "hi\n",
                ("fail",): FakeProcess(stderr="boom", returncode=1),
            }
        )
        res = fake.run("echo", "hi")
        self.assertEqual(res.stdout, "hi\n")
        self.assertEqual(fake.calls, [("echo", "hi")])

        with self.assertRaises(subprocess.CalledProcessError):
            fake.run("fail")

        failed_res = fake.run("fail", check=False)
        self.assertEqual(failed_res.returncode, 1)


if __name__ == "__main__":
    unittest.main()
