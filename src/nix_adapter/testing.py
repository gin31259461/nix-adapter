"""Test utilities and mock classes for adapters."""

from __future__ import annotations
import subprocess
from typing import Any


class FakeProcess:
    """Mock CompletedProcess return value."""

    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class FakeNative:
    """Mock runner for Native commands in adapter tests."""

    def __init__(
        self,
        available_commands: set[str] | list[str] | None = None,
        responses: dict[tuple[str, ...], FakeProcess | str] | None = None,
    ):
        self.calls: list[list[str]] = []
        self.available_commands = set(available_commands or [])
        self.responses: dict[tuple[str, ...], FakeProcess] = {}
        if responses:
            for k, v in responses.items():
                if isinstance(v, str):
                    self.responses[k] = FakeProcess(stdout=v)
                else:
                    self.responses[k] = v

    def available(self, command: str) -> bool:
        return command in self.available_commands

    def run(self, *argv: str, **kwargs: Any) -> FakeProcess:
        self.calls.append(list(argv))
        cmd = tuple(argv)
        res = self.responses.get(cmd, FakeProcess())
        check = kwargs.get("check", True)
        allow_failure = kwargs.get("allow_failure", False)
        if check and not allow_failure and res.returncode != 0:
            raise subprocess.CalledProcessError(
                res.returncode, list(argv), res.stdout, res.stderr
            )
        return res
