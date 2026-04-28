# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip for this fixer commit, not the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` two-file slice. Implementation-file accounting covers the actual branch tip relative to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, including all follow-up implementation, test, scope-check, and handoff commits.
- Scope: CLI command-contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: current Milestone 3 CLI compatibility for the engine-first workflow loop, and the active MVP emphasis on `feat-commands`.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface; this handoff does not claim auditable state, persistence, retrieval, provider routing, Textual work, or A2UI schema progress.
- Architecture alignment: `ARCHITECTURE.md` assigns `src/qual/commands/**` to command-level behavior and output contracts; command code may call public `drafting`, `context`, and `engine` entrypoints, must not directly mutate persistent storage, and must keep provider routing centralized in engine policy modules.
- Scope boundary: this handoff claims deterministic CLI command-surface hardening only. It does not claim retrieval, persistence, provider routing, apply/reject engine execution, or `feat-console` progress.

## Reviewed Files

- `scripts/scope-check.sh`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `src/qual/commands/workflow.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Budget / Size Accounting

- Task budget: `4`; tasks completed: `4`.
- High-risk size limit status: exceeded and routed for reviewer/integrator exception instead of normal lane approval.
- Implementation range accounting for the actual submitted tip relative to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: `12 files changed, 12853 insertions(+), 983 deletions(-)` before this metadata-only fixer update.
- Reason for exception routing: branch history already includes command catalog expansion, parser surface alignment, workflow helpers, diff-preview hardening, scope-check accommodation, and shared unit tests.

## Shared / Approval Notes

- Reviewer-requested narrow-slice clarification: the `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog implementation slice touched no integrator-locked files. Its only non-owned implementation path was `tests/unit/test_commands_catalog.py`, the approved shared-by-approval test exception.
- Actual-tip shared/integrator-locked exception: `src/qual/cli.py`, explicitly listed as shared-by-approval for `codex/feat-commands*` and integrator-locked in `THREAD_OWNERSHIP.md`; included because the live argparse entrypoint surface must match the command catalog.
- No other integrator-locked files were touched in the actual submitted tip.
- Shared support edit: `scripts/scope-check.sh`, included to keep scope enforcement aligned with approved shared command tests.
- Approved shared test edits: `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, used as command-surface regression coverage for this lane.
- Shared-test approval context: the reviewer packet being fixed included an `Approved exception note` naming `tests/unit/test_commands_catalog.py` as the approved shared-test exception; this packet preserves that context and separately lists `tests/unit/test_diff_preview.py` as shared command-surface regression coverage included in the actual branch tip.

## Canonical Demo-Path Mapping

- Task 1 advances `continue working`: stable parser/catalog contracts keep command dispatch deterministic across follow-up operator turns.
- Task 2 advances `continue working`: alias-only parser drift now fails fast before an operator continues through a changed command surface.
- Task 3 advances `plan/revise` and `apply/reject patch`: command workflow and diff-preview regression coverage preserves the command surfaces used to revise plans and inspect patch choices.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact review basis needed to keep the branch moving without scope ambiguity.
- Final demo-path statement: this handoff most directly makes `continue working` more real by hardening the CLI command contract that preserves deterministic follow-on operation in the engine-first MVP loop.

## Reviewer Fix Satisfaction

1. Required fix 1 is satisfied by making the full actual branch tip the only review basis and explicitly excluding the older narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice as the review target.
2. Required fix 2 is satisfied by listing every changed implementation, test, scope-check, and handoff file, and by calling out `src/qual/cli.py`, `scripts/scope-check.sh`, and the shared tests with approval/exception context.
3. Required fix 3 is satisfied by replacing normal budget-compliance claims with high-risk accounting: `12 files changed, 12853 insertions(+), 983 deletions(-)` before this metadata-only fixer update, with reviewer/integrator exception routing required.
4. Required fix 4 is satisfied by the per-task canonical demo-path mapping and the final pre-handoff statement naming `continue working` as the demo-path step made more real.
5. Required fix 5 is satisfied by rerunning and reporting the full required gate sequence against this regenerated full-tip review basis.

## Reviewer-Fix Closure

- Reviewer packet `fixer__feat-commands__20260428T195234Z` requested actual-tip traceability, complete file accounting, high-risk size exception routing, per-task demo-path mapping, and fresh gate evidence.
- This closure records those fixes and reran the required gates for the final handoff state.
- Reviewer packet `fixer__feat-commands__20260428T195448Z` approved the branch with no required fixes; this fixer pass records that approval state and refreshes the required gate evidence.
- Reviewer packet `fixer__feat-commands__20260428T195731Z` repeated the earlier required-fix packet; this fixer pass verified the existing full parser-projection guard, actual-tip handoff basis, shared exception accounting, and demo-path mapping, then reran every required gate.

## Required Gates

- Final fixer validation sequence for this regenerated packet:
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_extra_alias_entrypoint_when_canonical_order_still_matches tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_reordered_parser_projection_when_tokens_change_but_names_do_not` -> passed
- `python -m unittest tests.unit.test_commands_catalog` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
- Final fixer validation sequence for `fixer__feat-commands__20260428T195731Z`:
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
