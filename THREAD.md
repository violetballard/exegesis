# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the existing canonical catalog surface, rejects alias-level and ordering drift across the grouped parser surface, and preserves the deterministic entrypoint projection the operator already uses.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, persistence or auditability work, or a new workflow capability.
- Canonical demo-path step advanced: the roadmap's `vault` step in the CLI MVP flow `vault -> context -> run -> patch -> export`, because this slice keeps the operator-facing `open project/document` entry surface deterministic before the workflow can enter vault-backed state through the CLI.
- Canonical MVP flow context: `ROADMAP.md` currently defines the CLI MVP flow as `vault -> context -> run -> patch -> export` against the same engine `PolicyGate`, and this slice only hardens the parser-backed command surface that operators use before that flow begins.
- Causal link: if the `open project/document` command surface drifts away from the canonical catalog without a hard failure, the operator cannot reliably enter the vault-backed CLI MVP flow at all; failing fast on parser/catalog drift hardens that gateway without adding a new workflow step.
- Explicit re-review statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract through alias substitution, missing canonical entrypoints, reordered grouped entrypoints, or extra parser-only aliases on the existing `open project/document` entry surface that operators use before the roadmap's `vault -> context -> run -> patch -> export` flow, preserving the CLI compatibility required by the current MVP roadmap.
- Step-1 strengthening sentence: deterministic CLI contract validation makes the roadmap's `vault` step more real because the exact parser-backed entrypoints the operator uses to open project or document state are now forced to match the canonical catalog before the CLI MVP flow can enter vault-backed state.
- Demo-path sentence: this change makes the existing CLI MVP path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog through alias-level or ordering changes before the rest of the `vault -> context -> run -> patch -> export` loop runs.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could begin the manual MVP flow through an `open project/document` surface that no longer matched the expected contract.
- Final fixer note: this pointer remains implementation-scoped to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current branch tip only refreshes the handoff after correcting the roadmap wording and rerunning the required gates from this fixer pass.
- Final verification note: this metadata-only fixer pass on `2026-04-24` revalidated the corrected handoff mapping against the current canonical roadmap wording and reran the full required gate set from the current branch tip without changing the reviewed implementation slice.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun successfully from the current branch tip in this metadata-only fixer handoff.
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
