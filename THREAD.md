# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Explicit re-review statement: this slice makes `preview and apply or reject a patch` more real in the CLI-first Milestone 3 loop because the `diff-preview` and `diff` patch-review entrypoints now fail fast if the parser surface drifts from the catalog instead of silently changing the operator contract while Textual remains disabled.
- Concrete blocker removed: patch-review CLI drift can no longer silently desynchronize the parser surface from the catalog while still appearing canonically ordered.
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
