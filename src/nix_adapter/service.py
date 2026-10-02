"""Base adapter for system and service reconciliation."""

from __future__ import annotations
from pathlib import Path
import stat
from typing import Any

from .exceptions import Conflict
from .native import Native
from .systemd import Systemd


class BaseServiceAdapter:
    def __init__(
        self,
        desired: dict[str, Any],
        root: Path = Path("/"),
        runner: Native | None = None,
    ):
        self.desired = desired
        self.root = root
        self.runner = runner or Native()
        self.systemd = Systemd(self.runner)

    def path(self, key: str) -> Path:
        value = self.desired.get(key)
        if (
            not isinstance(value, str)
            or not value.startswith("/")
            or ".." in Path(value).parts
        ):
            raise Conflict(f"invalid manifest path for {key}")
        return self.root / value.lstrip("/")

    def validate_file(self, key: str, mode_mask: int = 0o022) -> Path:
        path = self.path(key)
        if path.is_symlink() or not path.is_file():
            raise Conflict(f"path {key} must be a regular file")
        info = path.stat()
        if info.st_nlink != 1 or (info.st_uid != 0 and self.root == Path("/")):
            raise Conflict(f"path {key} has unsafe ownership")
        if stat.S_IMODE(info.st_mode) & mode_mask:
            raise Conflict(f"path {key} has unsafe permissions")
        return path
