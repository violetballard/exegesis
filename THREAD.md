# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip, not the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice. Implementation-file accounting covers `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..f175b28266c0981c89c20f74b31c37c25f232277` plus the reviewer-fix and handoff metadata correction commits.
- Scope: CLI command-contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: `ROADMAP.md` Milestone 1 `Command and diff-preview behavior hardening` / `Manual CLI smoke flow remains stable`, Milestone 2 remaining parser-edge coverage, Milestone 3 output-contract intentionality, and the active MVP emphasis on `feat-commands`.
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`.
- Scope boundary: this handoff claims deterministic CLI command-surface hardening only. It does not claim retrieval, persistence, provider routing, apply/reject engine execution, or Textual UI progress.

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
- Implementation range accounting: `12 files changed, 12561 insertions(+), 927 deletions(-)` from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..f175b28266c0981c89c20f74b31c37c25f232277`.
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

1. `command_cli_contract()` validates the full parser/catalog projection: declared entrypoints, live parser entrypoints, canonical-name order, accepted CLI tokens, lookup rows, and reconstructed grouped projection.
2. `tests/unit/test_commands_catalog.py` includes alias-only parser drift coverage where canonical names remain stable but parser tokens or lookup rows change.
3. `THREAD_PACKET.md` and `handoff_packets/feat-commands.md` now review the actual branch tip and do not label test or implementation changes as metadata-only.
4. Each numbered completed task names the canonical demo-path step it supports, with `continue working` called out as the step made most real.
5. The full required gates were rerun after the corrected implementation and packet were in place.

## Required Gates

- Latest fixer evidence timestamp: `2026-04-28T19:01:20Z`
- `python -m unittest tests.unit.test_commands_catalog` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
