# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py` plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift.
- Canonical demo-path step advanced: `continue working without losing context` in the CLI-first engine loop.
- Explicit re-review statement: this `feat-commands` CLI-contract hardening slice strengthens `continue working without losing context` by preserving the operator-facing CLI command catalog contract that this step depends on while Textual remains disabled.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so the operator could reach `continue working without losing context` with a command surface that no longer matched the expected CLI contract for that step.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Shared-test approval reference: `scripts/scope-check.sh` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`.

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
