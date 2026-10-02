# AGENTS Instructions

Work in this standalone Python + Nix library repository.

## Ownership and contracts

- `nix-adapter` provides core reconciliation primitives (`Native`, `Files`, `Conflict`).
- Keep external pip dependencies at zero: strictly standard-library only.
- All code must pass `python -m unittest discover -s tests` and `nix flake check`.
