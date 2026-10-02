"""TOML parsing utilities using standard library tomllib."""

from __future__ import annotations
from pathlib import Path
import tomllib
from typing import Any


def parse_toml(content: str | bytes) -> dict[str, Any]:
    """Parse TOML content from a string or bytes."""
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return tomllib.loads(content)


def read_toml(path: Path | str) -> dict[str, Any]:
    """Read and parse a TOML file."""
    with open(path, "rb") as stream:
        return tomllib.load(stream)
