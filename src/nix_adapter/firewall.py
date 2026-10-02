"""UFW status parsing and netfilter rule inspection primitives."""

from __future__ import annotations
import re
from typing import Any

from .exceptions import Conflict
from .native import Native


def format_port_range(from_port: int | str, to_port: int | str | None = None) -> str:
    """Format a port or port range as a string like '80' or '27031:27036'."""
    return str(from_port) if to_port is None or to_port == from_port else f"{from_port}:{to_port}"


def parse_ufw_status(text: str) -> dict[str, Any]:
    """Parse 'ufw status verbose' output into structured policy and rules."""
    if text.strip() == "Status: inactive":
        return {"active": False, "rules": set()}
    if not text.startswith("Status: active\n"):
        raise Conflict("unrecognized UFW status")

    policy = re.search(
        r"^Default: (deny|allow|reject) \(incoming\), (deny|allow|reject) \(outgoing\), (deny|allow|reject|disabled) \(routed\)$",
        text,
        re.M,
    )
    logging = re.search(r"^Logging: (off|on \((low|medium|high|full)\))$", text, re.M)
    profiles = re.search(r"^New profiles: (skip|allow|deny|reject)$", text, re.M)
    if not policy or not logging or not profiles:
        raise Conflict("incomplete UFW status")

    rules: set[tuple[str, str, bool]] = set()
    for line in text.splitlines():
        match = re.fullmatch(
            r"(\d+(?::\d+)?)/(tcp|udp)\s*(\(v6\))?\s+ALLOW IN\s+Anywhere(?: \(v6\))?\s*(?:#.*)?",
            line,
        )
        if match:
            port, protocol, v6 = match.groups()
            rules.add((port, protocol, bool(v6)))
        elif re.search(r"\b(DENY|REJECT|LIMIT)\b", line):
            raise Conflict(
                "UFW has restrictive rules requiring explicit ownership review"
            )

    return {
        "active": True,
        "rules": rules,
        "policy": policy.groups(),
        "logging": logging[2] or "off",
        "profiles": profiles[1],
    }


def check_kernel_rule(
    chain: str,
    protocol: str,
    port: str,
    v6: bool = False,
    runner: Native | None = None,
) -> bool:
    """Check if a specific port acceptance rule is loaded in the netfilter chain."""
    r = runner or Native()
    command = "ip6tables" if v6 else "iptables"
    match = ["-m", "multiport", "--dports", port] if ":" in port else ["--dport", port]
    return (
        r.run(
            command,
            "-w",
            "5",
            "-C",
            chain,
            "-p",
            protocol,
            *match,
            "-j",
            "ACCEPT",
            check=False,
        ).returncode
        == 0
    )


def check_kernel_policy(runner: Native | None = None) -> bool:
    """Verify that default kernel policies for INPUT, OUTPUT, FORWARD match UFW defaults."""
    r = runner or Native()
    for command in ("iptables", "ip6tables"):
        for chain, policy in (
            ("INPUT", "DROP"),
            ("OUTPUT", "ACCEPT"),
            ("FORWARD", "DROP"),
        ):
            result = r.run(command, "-w", "5", "-S", chain, check=False)
            if (
                result.returncode
                or f"-P {chain} {policy}" not in result.stdout.splitlines()
            ):
                return False
    return True
