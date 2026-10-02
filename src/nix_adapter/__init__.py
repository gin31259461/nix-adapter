"""Cross-platform native reconciliation adapter for Nix deployments."""

from .exceptions import Conflict, NotReady
from .files import Files, assignments, ini, locale_gen, replace_keys
from .native import Native

__version__ = "0.1.0"

__all__ = [
    "Conflict",
    "Files",
    "Native",
    "NotReady",
    "assignments",
    "ini",
    "locale_gen",
    "replace_keys",
]
