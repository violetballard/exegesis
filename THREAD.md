# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the existing canonical catalog surface, rejects alias-level and ordering drift across the grouped parser surface, and preserves the deterministic entrypoint projection the operator already uses.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, persistence or auditability work, or a new workflow capability.
- Canonical demo-path step advanced: `open project/document` in the active AGENTS demo path, because this slice keeps the operator-facing CLI entry surface deterministic at the point where the Milestone 3 loop begins.
- Canonical demo-path context: `AGENTS.md` currently defines the engine-side path as `open project/document` -> `retrieve relevant material` -> `promote or gather context into the basket` -> `produce a plan or revision` -> `preview and apply or reject a patch` -> `persist the updated document/session state` -> `continue working without losing context`.
- Causal link: if the `open project/document` command surface drifts away from the canonical catalog without a hard failure, the operator cannot reliably start the Milestone 3 CLI loop at all; failing fast on parser/catalog drift hardens that gateway without claiming any broader workflow advancement.
- Explicit re-review statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract through alias substitution, missing canonical entrypoints, reordered grouped entrypoints, or extra parser-only aliases on the existing `open project/document` surface, preserving the CLI compatibility Milestone 3 requires while Textual remains disabled.
- Step strengthening sentence: deterministic CLI contract validation makes the `open project/document` step more real because the exact parser-backed entrypoints the operator uses to start the workflow are now forced to match the canonical catalog before the rest of the loop begins.
- Demo-path sentence: this change makes the existing CLI path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog through alias-level or ordering changes.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could begin the active Milestone 3 flow through an `open project/document` surface that no longer matched the expected contract.
- Final fixer note: this pointer remains implementation-scoped to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer pass only refreshes the handoff after tightening the Milestone 3 CLI-compatibility wording and rerunning the required gates.
- Final verification note: this metadata-only fixer rerun on `2026-04-24` rechecked the corrected handoff mapping against the current Milestone 3 CLI-compatibility wording and reran the full required gate set without changing the reviewed implementation slice.
- Latest fixer rerun note: the live worktree was re-read from the reviewer packet on `2026-04-24` before this follow-up, and the refresh remained metadata-only because the required implementation and regression coverage were already present on `codex/feat-commands`.
- Current fixer pass note: this follow-up pass rechecked the live reviewed implementation files, verified that the parser-surface guardrail and alias-drift regressions were already present, and kept the new work limited to handoff metadata refresh plus another required-gates rerun.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun successfully again in this metadata-only fixer handoff.
- Shared-test approval provenance: the only non-owned implementation path, `tests/unit/test_commands_catalog.py`, is covered by the integrator-managed `codex/feat-commands` branch policy and the integrator/release ownership gate recorded locally in `scripts/scope-check.sh` under `is_approved_shared_test()` for `codex/feat-commands*`.
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
