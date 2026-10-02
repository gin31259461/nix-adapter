"""Cross-platform native reconciliation adapter and CLI primitives for Nix deployments."""

from .exceptions import Conflict, NotReady
from .files import Files, assignments, ini, locale_gen, replace_keys
from .io import (
    atomic_write,
    directory_fd,
    ensure_directory,
    read_managed,
    regular_file,
    remove_managed_file,
)
from .lock import operation_lock
from .native import Native
from .progress import Progress, Task
from .service import BaseServiceAdapter
from .systemd import Systemd

__version__ = "0.2.0"

__all__ = [
    "BaseServiceAdapter",
    "Conflict",
    "Files",
    "Native",
    "NotReady",
    "Progress",
    "Systemd",
    "Task",
    "assignments",
    "atomic_write",
    "directory_fd",
    "ensure_directory",
    "ini",
    "locale_gen",
    "operation_lock",
    "read_managed",
    "regular_file",
    "remove_managed_file",
    "replace_keys",
]
