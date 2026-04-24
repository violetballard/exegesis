# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py` plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift.
- Canonical MVP flow advanced: `project-open -> retrieval -> patch-review -> export-handoff` for the manual CLI smoke flow.
- Explicit re-review statement: this `feat-commands` CLI-contract hardening slice strengthens `project-open -> retrieval -> patch-review -> export-handoff` by preserving the operator-facing CLI command catalog contract that the manual smoke flow depends on while CLI remains the active first-class surface.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could run `project-open -> retrieval -> patch-review -> export-handoff` through a command surface that no longer matched the expected contract.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Shared-test approval reference: `scripts/scope-check.sh` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`.
- Shared-edit checkpoint reference: `THREAD_PACKET.md` now preserves the high-risk `before risky/shared file edit` checkpoint stating that the shared regression path was verified against the branch allowlist before shared handoff metadata was refreshed.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
