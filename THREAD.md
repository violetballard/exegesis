# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the existing canonical catalog surface, rejects alias-level and ordering drift across the grouped parser surface, and preserves the deterministic entrypoint projection the operator already uses.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, persistence or auditability work, or a new workflow capability.
- Canonical demo-path step advanced: the already-modeled CLI-first MVP loop that starts with `open project/document` and continues through `retrieve relevant material` to `preview and apply or reject a patch`, by tightening the existing parser/catalog contract for the command surface that starts that loop while Textual remains disabled rather than expanding loop reachability.
- Canonical MVP flow context: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` remains the same manual CLI smoke flow, and this slice only hardens the existing parser-backed command surface that starts and therefore gates that path so the CLI can still execute the MVP loop while Textual remains disabled.
- Explicit re-review statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract through alias substitution, missing canonical entrypoints, reordered grouped entrypoints, or extra parser-only aliases on the existing `open project/document` entry surface that starts the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop, preserving the CLI compatibility required while Textual remains disabled and the Milestone 3 exit criterion that `CLI can still execute the MVP loop while Textual remains disabled`.
- Demo-path sentence: this change makes the existing CLI-first MVP path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog through alias-level or ordering changes before the rest of the loop runs, which keeps the downstream `retrieve relevant material` and `preview and apply or reject a patch` steps reachable through the same deterministic CLI loop while Textual remains disabled.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could begin the manual MVP flow through an `open project/document` surface that no longer matched the expected contract.
- Final fixer note: this pointer remains implementation-scoped to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current branch tip only refreshes the handoff after another green rerun of the required gates from this fixer pass.
- Final verification note: a metadata-only fixer pass on `2026-04-24` revalidated the corrected handoff mapping and reran the full required gate set from the current branch tip without changing the reviewed implementation slice.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun successfully from the current branch tip before this metadata-only fixer handoff.
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
