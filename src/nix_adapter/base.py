"""Base adapter class defining standard lifecycle and resource contracts."""

from __future__ import annotations
from pathlib import Path
from typing import Any

from .exceptions import Conflict
from .files import Files
from .native import Native
from .systemd import Systemd


class BaseAdapter:
    """Unified base adapter for system settings, services, and multi-service reconciliation."""

    def __init__(
        self,
        desired: dict[str, Any],
        root: Path | str = Path("/"),
        runner: Native | None = None,
        files: Files | None = None,
    ):
        self.desired = desired
        self.root = Path(root)
        self.runner = runner or Native()
        self.files = files or Files(self.root)
        self.systemd = Systemd(self.runner)
        self.updates: int = 0
        self.actions: int = 0

    @property
    def native(self) -> Native:
        """Backwards-compatibility alias for self.runner."""
        return self.runner

    @native.setter
    def native(self, value: Native) -> None:
        self.runner = value
        self.systemd = Systemd(self.runner)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        return self.runner.run(*args, **kwargs)

    def unit(self, name: str) -> dict[str, str]:
        """Inspect unit state properties."""
        return self.systemd.show(
            name, properties=["LoadState", "ActiveState", "UnitFileState"]
        )

    def ready_unit(self, name: str) -> dict[str, str]:
        """Verify that a unit is loaded and not masked."""
        state = self.unit(name)
        if state.get("LoadState") != "loaded" or state.get("UnitFileState") in (
            "masked",
            "masked-runtime",
        ):
            raise Conflict(f"required system unit is missing or masked: {name}")
        return state

    def require_unit(self, name: str) -> dict[str, str]:
        """Alias for ready_unit."""
        return self.ready_unit(name)

    def path(self, key: str, default: str | None = None) -> Path:
        """Resolve a declared path relative to root, checking paths dictionary or direct keys."""
        value = None
        paths = self.desired.get("paths")
        if isinstance(paths, dict):
            value = paths.get(key)
        if value is None:
            value = self.desired.get(key)
        if value is None and default is not None:
            value = default
        if (
            not isinstance(value, str)
            or not value.startswith("/")
            or ".." in Path(value).parts
        ):
            raise Conflict(f"invalid manifest path for {key}")
        return self.root / value.lstrip("/")

    def write(
        self, path: str | Path, text: str, action: str, mode: int = 0o644
    ) -> bool:
        """Write managed configuration atomically and record updates and pending state."""
        p_str = str(path)
        if not self.files.matches(p_str, text, mode=mode):
            self.files.mark(action)
            changed = self.files.write(p_str, text, mode=mode)
            self.updates += int(changed)
            return changed
        return False

    def preflight(self, installed: bool = False) -> bool | None:
        """Validate prerequisites before convergence."""
        return None

    def converge(self) -> None:
        """Reconcile state to match desired configuration."""
        pass
