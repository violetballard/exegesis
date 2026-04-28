# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip after this reviewer-fix commit, not the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` two-file slice. Implementation-file accounting covers the actual branch tip relative to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, including all follow-up implementation, test, scope-check, and handoff commits.
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
- Implementation range accounting before this reviewer-fix metadata update: `12 files changed, 12838 insertions(+), 982 deletions(-)` from the actual branch tip relative to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
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

1. Required fix 1 is satisfied by `command_cli_contract()` validating the declared catalog entrypoint projection, live parser projection, contract token tuple, canonical-name tuple, and lookup table; regression coverage includes extra alias token drift and alias-first reordering with stable canonical names.
2. Required fix 2 is satisfied by the per-task canonical demo-path mapping in `THREAD_PACKET.md`.
3. Required fix 3 is satisfied by the pre-handoff demo-path readiness line in `THREAD_PACKET.md`: this command-catalog contract makes `continue working` more real by removing silent parser/catalog drift as a blocker for deterministic follow-up CLI operator turns.
4. Required fix 4 is satisfied by the ownership clarification above and the shared-test approval context: the reviewed `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice touched no integrator-locked files, and the reviewer packet explicitly carried an approved shared-test exception for `tests/unit/test_commands_catalog.py`. The packet still separately preserves actual-tip shared/integrator-locked accounting for `src/qual/cli.py`.

## Reviewer-Fix Closure

- Reviewer packet `fixer__feat-commands__20260428T193229Z` requested actual-tip traceability, complete file accounting, shared/integrator-locked exceptions, high-risk size exception routing, and per-task demo-path mapping.
- This closure records those fixes and reran the required gates for the final handoff state.

## Required Gates

- Latest fixer evidence timestamp: `2026-04-28T19:46:51Z`
- `python -m unittest tests.unit.test_commands_catalog` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
