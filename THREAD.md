# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift
- Canonical demo-path step advanced: `continue working without losing context` in the CLI-first engine loop.
- Explicit re-review statement: this Milestone 3 CLI-contract hardening slice directly strengthens `continue working without losing context` by forcing the active CLI command contract to stay deterministic while Textual remains disabled.
- Concrete blocker removed: once the operator is in the engine-first loop, parser drift can no longer silently desynchronize the CLI contract from the canonical catalog and then break the operator's ability to continue working against the expected CLI command surface for that step.
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
