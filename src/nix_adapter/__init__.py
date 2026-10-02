"""Cross-platform native reconciliation adapter and CLI primitives for Nix deployments."""

from .cli import run_adapter_cli
from .exceptions import Conflict, NotReady
from .files import Files, assignments, ini, locale_gen, replace_keys
from .firewall import (
    FirewallBackend,
    FirewalldBackend,
    UfwBackend,
    canonical_rule,
    check_kernel_policy,
    check_kernel_rule,
    format_port_range,
    hotspot_firewall_rules,
    parse_ufw_status,
)
from .hotspot import (
    HotspotManager,
    check_hotspot_prerequisites,
    find_hotspot_connection_uuid,
    hotspot_properties,
    is_hotspot_active,
    validate_hotspot_address,
)
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
from .base import BaseAdapter
from .service import BaseServiceAdapter
from .system import (
    check_discard_support,
    get_hostname,
    get_timezone,
    is_ntp_synchronized,
    set_hostname,
    set_timezone,
)
from .systemd import Systemd
from .toml import parse_toml, read_toml

__version__ = "0.3.0"

__all__ = [
    "BaseAdapter",
    "BaseServiceAdapter",
    "Conflict",
    "Files",
    "FirewallBackend",
    "FirewalldBackend",
    "HotspotManager",
    "Native",
    "NotReady",
    "Progress",
    "Systemd",
    "Task",
    "UfwBackend",
    "assignments",
    "atomic_write",
    "canonical_rule",
    "check_discard_support",
    "check_hotspot_prerequisites",
    "check_kernel_policy",
    "check_kernel_rule",
    "directory_fd",
    "ensure_directory",
    "find_hotspot_connection_uuid",
    "format_port_range",
    "get_hostname",
    "get_timezone",
    "hotspot_firewall_rules",
    "hotspot_properties",
    "ini",
    "is_hotspot_active",
    "is_ntp_synchronized",
    "locale_gen",
    "operation_lock",
    "parse_toml",
    "parse_ufw_status",
    "read_managed",
    "read_toml",
    "regular_file",
    "remove_managed_file",
    "replace_keys",
    "run_adapter_cli",
    "set_hostname",
    "set_timezone",
    "validate_hotspot_address",
]
