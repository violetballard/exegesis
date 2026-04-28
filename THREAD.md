# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip after this reviewer-fix commit, not the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` two-file slice. Implementation-file accounting covers the actual branch tip relative to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, including all follow-up implementation, test, scope-check, and handoff commits.
- Scope: CLI command-contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: `ROADMAP.md` Milestone 1 `Command and diff-preview behavior hardening` / `Manual CLI smoke flow remains stable`, Milestone 2 remaining parser-edge coverage, Milestone 3 output-contract intentionality, and the active MVP emphasis on `feat-commands`.
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`.
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
- Implementation range accounting before this reviewer-fix metadata update: `12 files changed, 12841 insertions(+), 982 deletions(-)` from the actual branch tip relative to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Reason for exception routing: branch history already includes command catalog expansion, parser surface alignment, workflow helpers, diff-preview hardening, scope-check accommodation, and shared unit tests.

## Shared / Approval Notes

- Integrator-locked edit: `src/qual/cli.py`, explicitly listed as shared-by-approval for `codex/feat-commands*` in `THREAD_OWNERSHIP.md`; included because the live argparse entrypoint surface must match the command catalog.
- No other integrator-locked files were touched.
- Shared support edit: `scripts/scope-check.sh`, included to keep scope enforcement aligned with approved shared command tests.
- Approved shared test edits: `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, used as command-surface regression coverage for this lane.

## Canonical Demo-Path Mapping

- Task 1 advances `continue working`: stable parser/catalog contracts keep command dispatch deterministic across follow-up operator turns.
- Task 2 advances `continue working`: alias-only parser drift now fails fast before an operator continues through a changed command surface.
- Task 3 advances `plan/revise` and `apply/reject patch`: command workflow and diff-preview regression coverage preserves the command surfaces used to revise plans and inspect patch choices.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact review basis needed to keep the branch moving without scope ambiguity.
- Final demo-path statement: this handoff most directly makes `continue working` more real by hardening the CLI command contract that preserves deterministic follow-on operation in the engine-first MVP loop.

## Reviewer Fix Satisfaction

1. Required fix 1 is satisfied by keeping the actual submitted branch tip as the review basis instead of the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
2. Required fix 2 is not the selected route; later implementation commits remain on this branch, so the packet does not claim a narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` review slice.
3. Required fix 3 is satisfied by listing every implementation file changed in the actual review range, including `src/qual/cli.py`, `scripts/scope-check.sh`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `src/qual/commands/workflow.py`, and both shared test files; the packet also records the shared/integrator-locked exceptions, high-risk size overage, and fresh gate evidence.
4. Required fix 4 is satisfied by the roadmap, vision, architecture, and AGENTS demo-path mapping in this packet.
5. Required fix 5 is satisfied by removing the earlier metadata-only contradiction and submitting this actual-tip packet for re-review.

## Reviewer-Fix Closure

- Reviewer packet `fixer__feat-commands__20260428T193229Z` requested actual-tip traceability, complete file accounting, shared/integrator-locked exceptions, high-risk size exception routing, and per-task demo-path mapping.
- This closure records those fixes and reran the required gates for the final handoff state.

## Required Gates

- Latest fixer evidence timestamp: `2026-04-28T19:39:03Z`
- `python -m unittest tests.unit.test_commands_catalog` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
