# nix-adapter

Cross-platform native reconciliation adapter for Nix deployments.

`nix-adapter` provides safe, atomic file operations, lossless diagnostics capture, and process execution primitives for reconciling native host operating system state against Nix-evaluated declarations.

## Architecture

- **`nix_adapter.Native`**: Safe host command runner with complete stdout/stderr diagnostics capture, execution timeouts, and redaction.
- **`nix_adapter.Files`**: Atomic file writes, SHA256 checksums, POSIX permissions, conflict detection, and systemd drop-in validation.
- **`nix_adapter.exceptions.Conflict`**: Safe diagnostic exception type preventing sensitive config leakage.

## Usage in Nix Flakes

```nix
{
  inputs = {
    nix-adapter.url = "github:gin31259461/nix-adapter";
  };

  outputs = { self, nixpkgs, nix-adapter, ... }: {
    # Access the Python interpreter preloaded with nix-adapter:
    # nix-adapter.packages.${system}.adapterPython
  };
}
```
