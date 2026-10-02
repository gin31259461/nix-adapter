"""Standard exceptions for nix-adapter."""


class Conflict(Exception):
    """A safe, fixed diagnostic; never embed raw configuration or command output."""


class NotReady(Exception):
    """Required operator-owned configuration has never been prepared."""
