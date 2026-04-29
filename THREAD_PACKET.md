# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit / review basis: current branch tip after this reviewer-fix commit.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewer packet addressed: `20260429T010722Z`

## Packet Traceability Note

- Review the actual `codex/feat-commands` branch tip. Do not treat commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only.
- The branch-tip implementation includes command-catalog code and test changes after `f8d860e`.
- This fixer pass removes the prior `scripts/scope-check.sh` scope-policy edit so no gate-policy file remains part of the net review diff.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - persistence floor for document, basket, vault, and session state.
2. `feat-commands` - stable CLI control surface for the engine-first MVP loop.
3. `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.
4. `feat-engine-runs` - close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition Of Done For This Lane

- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

## Do Not Spend Time On

- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

## Lane / Owned Paths

- `src/qual/commands/**`

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full parser-visible command surface against the canonical CLI surface.
- Preserved canonical command ordering by keeping CLI canonical names aligned with `command_names()`.
- Rejected parser drift for added aliases, removed aliases, same-canonical substitutions, token reordering, lookup-table shape drift, lookup-table order drift, and declared-surface drift.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for accepted-alias drift such as `open` for `bootstrap` and `diff_preview` for `diff-preview`.
- Reconciled the handoff packet so the review basis is the actual branch tip and the file/accounting list matches the branch-tip implementation.

## Canonical Demo-Path Step Advanced

- This makes the open/retrieve/basket/patch-review CLI smoke path more real by keeping the parser-visible command contract deterministic and failing fast when parser tokens drift from the command catalog.
- Protected command steps:
  - `project-open`: `bootstrap` remains the only parser-visible project-open token.
  - `retrieval`: `context-basket` remains the parser-visible basket/retrieval token.
  - `patch-review`: `diff-preview` and compatibility alias `diff` remain the only parser-visible patch-review tokens.
  - `export-handoff`: `terminal` remains the parser-visible export/handoff token.

## Kickoff Budget / Limits Accounting

- Risk level: `HIGH`, because command-surface contract behavior and shared test coverage are in scope.
- High-risk task cap: `4`; completed `4` meaningful tasks.
- Size/file accounting for the actual branch-tip review basis is no longer represented as a metadata-only slice after `f8d860e`; code and tests after that commit are part of review.
- Net reviewed files after this fixer pass:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Removed from net review diff by this fixer pass:
  - `scripts/scope-check.sh`

## Approved Exception Note

- Lane-owned implementation edit: `src/qual/commands/catalog.py`.
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval edits: YES, `tests/unit/test_commands_catalog.py` under approved exception.
- Integrator-locked edits: NO.
- Gate-policy edits: NO net change after this fixer pass.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify the parser surface against the canonical CLI surface and reject parser/catalog drift for the `project-open`, `retrieval`, `patch-review`, and `export-handoff` CLI smoke path.
2. Preserved canonical command ordering in the CLI contract by returning names aligned with `command_names()` for `bootstrap`, `diff-preview`, `context-basket`, and `terminal`.
3. Added regression coverage for added aliases, removed aliases, same-canonical substitutions, token reordering, lookup-table shape/order drift, and declared-surface drift, including `open` for the `project-open` step and `diff_preview` for the `patch-review` step.
4. Reconciled the branch-tip packet/accounting for `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`, and removed the unrelated `scripts/scope-check.sh` scope-policy edit from the net diff.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

### Removed From Net Diff

- `scripts/scope-check.sh`

## Commands Run + Outcomes

- `python -m pytest tests/unit/test_commands_catalog.py`: BLOCKED, active `/opt/homebrew/opt/python@3.14/bin/python3.14` does not have `pytest`; repo gate scripts below were used as authoritative validation.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS (144 tests)
- `./typecheck-test.sh`: PASS
- `make ci`: PASS (scope-check, format, lint, compile/typecheck, and quality-test)

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none.

## Required Handoff Fields

### Branch Name

- `codex/feat-commands`

### Scope Completed

- Command-catalog contract validation now keeps CLI canonical names aligned with the canonical command order and rejects parser/catalog drift across the full parser-visible CLI surface.

### Files Changed

- Listed above.

### Commands Run With Results

- Listed above.

### Risks / Blockers

- Listed above.

### Roadmap Item(s) Affected

- Milestone 3: real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision Capability Affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing / Provider Impact Note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-Check / Ownership Note

- Shared-by-approval edits: YES, `tests/unit/test_commands_catalog.py` under approved exception.
- Integrator-locked edits: NO.
- Gate-policy edits: NO net change after this fixer pass.

## Reviewer Packet `20260429T010722Z` Fix Satisfaction

1. Parser-surface drift validation: satisfied by comparing CLI tokens, lookup table, grouped parser surface, declared surface, and canonical names against the explicit canonical CLI parser surface.
2. Same-canonical parser drift coverage: satisfied by tests for replacing/adding `bootstrap` with `open` and replacing `diff` with `diff_preview`, plus lookup-table substitution coverage.
3. Branch-tip packet accounting: satisfied by listing `THREAD.md` and `THREAD_PACKET.md` as metadata-only handoff files and the command catalog/test files as reviewed implementation files.
4. Demo-path mapping: satisfied by naming the protected `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps in the task list and demo-path section.
5. Scope discipline: satisfied by keeping the net review scope to `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`; no provider/routing/Textual behavior is added.
6. Required gates: satisfied by rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` against this reviewer-fix worktree state.
