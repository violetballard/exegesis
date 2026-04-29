# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit / review basis: current branch tip after the `20260429T015007Z` fixer validation commit.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewer packet addressed: `20260429T015007Z`

## Packet Traceability Note

- Review the actual `codex/feat-commands` branch tip. Do not treat commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only.
- The branch-tip implementation includes command package, command-catalog, diff-preview command, and focused test changes after `f8d860e`.
- This fixer pass keeps `scripts/scope-check.sh` aligned with the branch review baseline, so no gate-policy file remains part of the net `main...HEAD` review diff.

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
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for accepted-alias drift such as `open` for `bootstrap`, `diff` replacing `diff-preview`, and `diff_preview` replacing `diff`.
- Reconciled the handoff packet so the review basis is the actual branch tip and the file/accounting list matches the branch-tip implementation.

## Canonical Demo-Path Step Advanced

- This command contract hardening strengthens the CLI surface for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by keeping those parser routes deterministic and drift-checked.
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
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Aligned with the branch review baseline by this fixer pass and excluded from the net `main...HEAD` review diff:
  - `scripts/scope-check.sh`

## Approved Exception Note

- Lane-owned implementation edit: `src/qual/commands/catalog.py`.
- Other lane-owned command edits: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/diff_preview.py`.
- Approved shared-test exceptions: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Shared-by-approval edits: YES, `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` under approved exception.
- Integrator-locked edits: NO.
- Gate-policy edits: NO net change after this fixer pass.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify the parser surface against the canonical CLI surface and reject parser/catalog drift for the `project-open`, `retrieval`, `patch-review`, and `export-handoff` CLI smoke path.
2. Preserved canonical command ordering in the CLI contract by returning names aligned with `command_names()` for `bootstrap`, `diff-preview`, `context-basket`, and `terminal`.
3. Added regression coverage for added aliases, removed aliases, same-canonical substitutions, token reordering, lookup-table shape/order drift, and declared-surface drift, including `open` for the `project-open` step and both `diff` and `diff_preview` replacement drift for the `patch-review` step.
4. Reconciled the branch-tip packet/accounting for `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`, and kept the unrelated `scripts/scope-check.sh` scope-policy edit out of the net `main...HEAD` review diff.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

### Restored To Review Baseline / Excluded From Net Diff

- `scripts/scope-check.sh`

## Commands Run + Outcomes

- `python -m pytest tests/unit/test_commands_catalog.py`: BLOCKED, active `/opt/homebrew/opt/python@3.14/bin/python3.14` does not have `pytest`; repo gate scripts below were used as authoritative validation.
- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran 145 unit tests, including same-canonical parser drift regressions for `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS; reran scope-check, format, lint, compileall, and the 145-test suite.
- `20260429T013834Z` fixer validation rerun: PASS for `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `20260429T014157Z` fixer validation rerun: PASS for `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `20260429T014429Z` fixer validation rerun: PASS for `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `20260429T014718Z` fixer validation rerun: PASS for `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `20260429T015007Z` fixer validation rerun: PASS for `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

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

- Shared-by-approval edits: YES, `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` under approved exception.
- Integrator-locked edits: NO.
- Gate-policy edits: NO net change after this fixer pass.

## Reviewer Packet `20260429T012436Z` Fix Satisfaction

1. Actual branch-tip review basis: satisfied by removing the metadata-only post-`f8d860e` framing and listing the current branch-tip diff.
2. Gate-policy diff: satisfied by restoring `scripts/scope-check.sh` to the branch review baseline, leaving no net gate-policy change in the `main...HEAD` review diff.
3. Files changed and ownership accounting: satisfied by listing the command package files, both focused tests, and metadata handoff files in the branch-tip review basis.
4. Demo-path mapping: satisfied by naming the protected `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps in the task list and demo-path section.
5. Required gates: satisfied by rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` against this reviewer-fix worktree state.

## Reviewer Packet `20260429T013303Z` Fix Satisfaction

1. `command_cli_contract()` validates the full parser-visible CLI token surface, not only de-duplicated canonical names. It compares canonical parser tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order.
2. Focused tests prove same-canonical parser drift is rejected, including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview` substitutions.
3. The packet is regenerated against the actual branch tip and does not classify test-changing commits as metadata-only.
4. Ownership accounting identifies `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` as approved shared-by-approval test edits. Integrator-locked edits: NO.
5. The canonical demo-path step mapping explicitly names the protected `project-open`, `retrieval`, `patch-review`, and `export-handoff` command steps.

## Reviewer Packet `20260429T013535Z` Fix Satisfaction

1. Demo-path alignment now states that this command contract hardening strengthens `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by keeping those parser routes deterministic and drift-checked.
2. Metadata-only files changed lists both `THREAD.md` and `THREAD_PACKET.md`, matching the packet refresh file set.
3. Implementation scope remains unchanged: no files beyond the command package files and focused command tests listed above are newly introduced by this reviewer-fix pass.

## Fixer Packet `20260429T013834Z` Validation

1. Required fix 1 remains satisfied by `command_cli_contract()` validating canonical parser tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order.
2. Required fixes 2 and 3 remain satisfied by focused tests for same-canonical substitutions, additions, removals, and reordering across `_CLI_ENTRYPOINTS`, declared surface, and lookup-table drift.
3. Required fix 4 remains satisfied by listing both metadata files and naming the canonical demo-path steps advanced by the work.
4. Required gates were rerun and passed for this fixer pass.

## Fixer Packet `20260429T014157Z` Validation

1. Required fix 1 remains satisfied by the actual branch-tip review basis: post-`f8d860e` command package, command-catalog, diff-preview command, focused test, and metadata changes are all included in this packet.
2. Required fix 2 remains satisfied by `command_cli_contract()` validating parser-visible tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order.
3. Required fix 3 remains satisfied by focused regressions for same-canonical substitution, token removal, token addition, and token reordering across `_CLI_ENTRYPOINTS`, declared surface, and lookup-table drift.
4. Required fix 4 remains satisfied because `scripts/scope-check.sh` is absent from the net `main...HEAD` review diff.
5. Required fix 5 remains satisfied by naming `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` in the canonical demo-path mapping.
6. Required gates were rerun and passed for this fixer pass.

## Fixer Packet `20260429T014429Z` Validation

1. Required fix 1 remains satisfied by `command_cli_contract()` comparing the full parser-visible CLI surface: canonical parser tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order.
2. Required fix 2 remains satisfied by focused tests that patch `_CLI_ENTRYPOINTS` and reject same-canonical substitutions, removed tokens, extra tokens, and reordered tokens.
3. Required fix 3 remains satisfied by the positive contract test proving `contract.tokens`, `contract.canonical_names`, and `contract.lookup_table` stay aligned with the declared canonical parser surface.
4. Required fix 4 remains satisfied by the canonical demo-path mapping for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
5. Required gates were rerun and passed for this fixer pass.

## Fixer Packet `20260429T014718Z` Validation

1. Required fix 1 remains satisfied by `command_cli_contract()` validating the parser-visible token surface, canonical lookup-table shape, grouped parser surface, declared surface, and canonical command order before returning the contract.
2. Required fix 2 remains satisfied by focused tests patching `_CLI_ENTRYPOINTS` for same-canonical substitutions, token removal, token addition, and token reordering.
3. Required fix 3 remains satisfied by this packet naming the actual branch tip as review basis and listing the branch-tip implementation files rather than treating post-`f8d860e` code/test changes as metadata-only.
4. Required fix 4 remains satisfied by the canonical demo-path mapping for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
5. Required gates were rerun and passed for this fixer pass.

## Fixer Packet `20260429T015007Z` Validation

1. Required fix 1 remains satisfied by `command_cli_contract()` validating the full parser-visible CLI surface, including added tokens, removed tokens, token reorder, lookup-table drift, and same-canonical alias substitution.
2. Required fix 2 remains satisfied by focused tests patching `_CLI_ENTRYPOINTS` for added alias tokens, removed tokens, token reordering, and same-canonical substitutions such as `bootstrap` -> `open` and `diff-preview` -> `diff`.
3. Required fix 3 remains satisfied by this packet naming the actual branch tip as review basis and listing branch-tip implementation files rather than treating post-`f8d860e` code/test changes as metadata-only.
4. Required fixes 4 and 5 remain satisfied by the files-changed and ownership accounting above, plus the canonical demo-path mapping for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
5. Required fix 6 is satisfied by the fresh validation rerun: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed.
