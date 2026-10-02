"""Unit tests for nix_adapter.firewall."""

import unittest
from unittest.mock import MagicMock

from nix_adapter.exceptions import Conflict
from nix_adapter.firewall import (
    check_kernel_policy,
    check_kernel_rule,
    format_port_range,
    parse_ufw_status,
)


class FirewallTests(unittest.TestCase):
    def test_format_port_range(self):
        self.assertEqual(format_port_range(80), "80")
        self.assertEqual(format_port_range(80, 80), "80")
        self.assertEqual(format_port_range(27031, 27036), "27031:27036")

    def test_parse_ufw_status_inactive(self):
        res = parse_ufw_status("Status: inactive\n")
        self.assertFalse(res["active"])
        self.assertEqual(res["rules"], set())

    def test_parse_ufw_status_active(self):
        sample = """Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80:443/tcp (v6)            ALLOW IN    Anywhere (v6)
"""
        res = parse_ufw_status(sample)
        self.assertTrue(res["active"])
        self.assertEqual(res["logging"], "low")
        self.assertEqual(res["profiles"], "skip")
        self.assertEqual(res["policy"], ("deny", "allow", "disabled"))
        self.assertIn(("22", "tcp", False), res["rules"])
        self.assertIn(("80:443", "tcp", True), res["rules"])

    def test_parse_ufw_status_restrictive_rule_conflict(self):
        sample = """Status: active
Logging: off
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     DENY IN     Anywhere
"""
        with self.assertRaises(Conflict):
            parse_ufw_status(sample)

    def test_check_kernel_rule(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.returncode = 0
        self.assertTrue(
            check_kernel_rule(
                "ufw-user-input", "tcp", "80", v6=False, runner=mock_runner
            )
        )
        mock_runner.run.assert_called_with(
            "iptables",
            "-w",
            "5",
            "-C",
            "ufw-user-input",
            "-p",
            "tcp",
            "--dport",
            "80",
            "-j",
            "ACCEPT",
            check=False,
        )

    def test_check_kernel_policy(self):
        mock_runner = MagicMock()
        mock_runner.run.return_value.returncode = 0
        mock_runner.run.return_value.stdout = "-P INPUT DROP\n-P OUTPUT ACCEPT\n-P FORWARD DROP\n"
        self.assertTrue(check_kernel_policy(runner=mock_runner))


if __name__ == "__main__":
    unittest.main()
