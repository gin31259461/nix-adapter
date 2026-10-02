"""Unit tests for nix_adapter.system."""

import tempfile
import unittest
from unittest.mock import MagicMock

from nix_adapter.exceptions import Conflict
from nix_adapter.system import (
    check_discard_support,
    get_hostname,
    get_timezone,
    is_ntp_synchronized,
    set_hostname,
    set_timezone,
)


class SystemUtilTests(unittest.TestCase):
    def test_get_and_set_timezone(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.stdout = "Timezone=UTC\nLocalRTC=no\n"
        with tempfile.TemporaryDirectory() as d:
            zone = get_timezone(runner=mock_runner, root=d)
            self.assertEqual(zone, "UTC")

        set_timezone("Asia/Taipei", runner=mock_runner)
        mock_runner.run.assert_called_with("timedatectl", "set-timezone", "Asia/Taipei")

    def test_get_timezone_local_rtc_conflict(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.stdout = "Timezone=UTC\nLocalRTC=yes\n"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(Conflict):
                get_timezone(runner=mock_runner, root=d)

    def test_get_and_set_hostname(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.stdout = "myhost\n"
        self.assertEqual(get_hostname(runner=mock_runner), "myhost")

        set_hostname("newhost", runner=mock_runner)
        mock_runner.run.assert_called_with("hostnamectl", "--static", "set-hostname", "newhost")

    def test_is_ntp_synchronized(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.stdout = "yes\n"
        self.assertTrue(is_ntp_synchronized(runner=mock_runner))

        mock_runner.run.return_value.stdout = "no\n"
        self.assertFalse(is_ntp_synchronized(runner=mock_runner))

    def test_check_discard_support(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.stdout = '{"blockdevices":[{"name":"nvme0n1","type":"disk","disc-max":2147483648,"mountpoints":["/"]}]}'
        self.assertTrue(check_discard_support(runner=mock_runner))

        mock_runner.run.return_value.stdout = '{"blockdevices":[{"name":"sda","type":"disk","disc-max":0,"mountpoints":["/"]}]}'
        with self.assertRaises(Conflict):
            check_discard_support(runner=mock_runner)


if __name__ == "__main__":
    unittest.main()
