# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the existing canonical catalog surface, preserves canonical command ordering, and rejects parser drift.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, persistence or auditability work, or a new workflow capability.
- Canonical demo-path step advanced: the already-modeled `open project/document` CLI entry step in the Milestone 3 CLI-first MVP loop, by making its existing parser/catalog contract deterministic while Textual remains disabled rather than expanding loop reachability.
- Canonical MVP flow context: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` remains the same manual CLI smoke flow, and this slice only hardens the existing parser-backed command surface that starts that path.
- Explicit re-review statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract for the existing `open project/document` entry surface required by Milestone 3's exit criterion that `CLI can still execute the MVP loop while Textual remains disabled`.
- Demo-path sentence: this change makes the existing CLI-first MVP path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog before the rest of the loop runs, tightening the CLI operator surface that keeps the MVP loop runnable while Textual remains disabled.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could begin the manual MVP flow through an `open project/document` surface that no longer matched the expected contract.
- Final fixer note: this pointer remains implementation-scoped to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current branch tip only refreshes the handoff after a green rerun of the required gates.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun successfully from the current branch tip before this metadata-only fixer handoff.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewed implementation files: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
