"""General Linux system administration and hardware inspection primitives."""

from __future__ import annotations
import json
import os
from pathlib import Path

from .exceptions import Conflict
from .native import Native


def get_timezone(runner: Native | None = None, root: Path | str = "/") -> str | None:
    """Read timezone from /etc/localtime and timedatectl."""
    root_path = Path(root)
    localtime_path = root_path / "etc/localtime"
    if localtime_path.exists() and not localtime_path.is_symlink():
        raise Conflict("localtime is not a zoneinfo symlink")
    if localtime_path.is_symlink():
        target = os.readlink(localtime_path)
        if not (
            target.startswith("/usr/share/zoneinfo/")
            or target.startswith("../usr/share/zoneinfo/")
        ) or ".." in target.removeprefix("../").split("/"):
            raise Conflict("localtime has an unexpected symlink target")

    r = runner or Native()
    values = r.run(
        "timedatectl",
        "show",
        "--property=Timezone",
        "--property=LocalRTC",
    ).stdout
    state = dict(line.split("=", 1) for line in values.splitlines() if "=" in line)
    if state.get("LocalRTC") != "no":
        raise Conflict("local RTC requires an explicit operator decision")
    return state.get("Timezone")


def set_timezone(timezone: str, runner: Native | None = None) -> None:
    """Set system timezone using timedatectl."""
    r = runner or Native()
    r.run("timedatectl", "set-timezone", timezone)


def get_hostname(runner: Native | None = None, kind: str = "--static") -> str:
    """Get system hostname using hostnamectl."""
    r = runner or Native()
    return r.run("hostnamectl", kind).stdout.strip()


def set_hostname(hostname: str, runner: Native | None = None, kind: str = "--static") -> None:
    """Set system hostname using hostnamectl."""
    r = runner or Native()
    r.run("hostnamectl", kind, "set-hostname", hostname)


def is_ntp_synchronized(runner: Native | None = None) -> bool:
    """Check if network time synchronization is currently active."""
    r = runner or Native()
    output = r.run(
        "timedatectl", "show", "--property=NTPSynchronized", "--value"
    ).stdout.strip()
    return output == "yes"


def check_discard_support(runner: Native | None = None) -> bool:
    """Inspect mounted block devices with lsblk to verify SSD trim/discard support."""
    r = runner or Native()
    data = json.loads(
        r.run(
            "lsblk",
            "--json",
            "--bytes",
            "--output",
            "NAME,TYPE,DISC-MAX,MOUNTPOINTS",
        ).stdout
    )

    def walk(devices: list[dict], encrypted: bool = False) -> bool:
        suitable = False
        for device in devices:
            crypt = encrypted or device.get("type") == "crypt"
            mounted = any(device.get("mountpoints") or [])
            if mounted and crypt:
                raise Conflict(
                    "encrypted mounted storage needs a separate discard policy"
                )
            suitable |= mounted and int(device.get("disc-max") or 0) > 0
            suitable |= walk(device.get("children", []), crypt)
        return suitable

    devices = data.get("blockdevices", [])
    if not walk(devices):
        raise Conflict("no mounted discard-capable device was found")
    return True
