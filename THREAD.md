# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift
- Canonical demo-path step advanced: `patch-review` in the CLI-first `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff` MVP loop.
- Explicit re-review statement: this slice makes `patch-review` more real in the CLI-first MVP loop because `command_cli_contract()` in `src/qual/commands/catalog.py` now returns the validated canonical parser-entrypoint projection instead of allowing a drifted parser surface to masquerade behind stable command names, and `tests/unit/test_commands_catalog.py` proves both the canonical `diff-preview`/`diff` ordering and the fail-fast rejection path that protects the live patch-review command contract while Textual remains disabled.
- Concrete blocker removed: after the operator opens a project or document and advances through retrieval, patch-review CLI drift can no longer silently desynchronize the parser surface from the catalog while still appearing canonically ordered.
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
