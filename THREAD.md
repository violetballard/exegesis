# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that locks `command_cli_contract()` to the canonical catalog and rejects parser-surface drift
- Canonical demo-path step advanced: `patch-review` in the CLI-first `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff` MVP loop.
- Explicit re-review statement: this slice makes `patch-review` more real in the CLI-first MVP loop because the operator still reaches that step through `project-open`/document open and retrieval before invoking `diff-preview` or `diff`, and those patch-review entrypoints now fail fast if the parser surface drifts from the catalog instead of silently changing the operator contract while Textual remains disabled.
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
