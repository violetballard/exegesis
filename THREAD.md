# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift
- Canonical demo-path step advanced: `continue working without losing context` in the CLI-first engine loop.
- Explicit re-review statement: this slice makes the `open project/document` and overall `continue working` command surface more reliable by keeping the canonical command contract deterministic while Textual remains disabled, because `command_cli_contract()` now depends on the validated projection returned from `_validated_cli_entrypoints_for()` and `_cli_entrypoints_by_name()` in `src/qual/commands/catalog.py`, and the imported regression surface in `tests/unit/test_commands_catalog.py` proves both the canonical catalog order and the fail-fast rejection path for parser drift.
- Concrete blocker removed: after the operator opens a project or document, command-surface drift can no longer silently desynchronize the CLI contract from the canonical catalog and then leak into the ongoing engine-first loop as the operator continues working.
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
