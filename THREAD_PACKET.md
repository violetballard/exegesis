# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: branch tip after fixer packet `20260429T033837Z`
- Implementation range: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Packet refresh role: reviewer-fix finalization for packet `20260429T033837Z`

## Packet Traceability Note

- Review the branch tip, not only `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` include non-metadata changes to `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; those files are part of this review basis.
- `THREAD.md` and `THREAD_PACKET.md` are metadata-only handoff files.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full parser surface, not only the de-duplicated canonical command names.
- Added canonical declared parser-surface projections for CLI tokens, lookup tables, and grouped token surfaces so drift in accepted aliases, missing tokens, reordered tokens, or same-canonical substitutions raises `ValueError`.
- Kept the returned contract aligned with the canonical command order by returning `command_names()` only after parser tokens and lookup tables validate against the declared canonical surface.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for full parser-surface drift, including same-canonical alias drift, missing expected tokens, reordered token surfaces, lookup-table drift, and declared-surface drift.
- Included the `scripts/scope-check.sh` change in this review basis instead of treating it as metadata-only.
- Regenerated the handoff packet with explicit canonical demo-path mapping for each completed task.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and lane size limits for the implementation slice.
- The implementation surface is limited to one lane-owned command file, one approved shared test file, and one shared tooling file now explicitly included for review.

## Approved Exception / Shared Scope Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- `scripts/scope-check.sh` is included as a shared tooling change in the review basis. It is scoped to lane scope-check behavior and does not touch runtime provider routing, engine entrypoints, CLI command behavior, or integrator-locked files.
- Integrator-locked edits: none.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
   - Demo-path mapping: all CLI-first demo steps, because the command contract is the dispatch floor for open, retrieve/basket, patch review, and terminal export while Textual remains disabled.
2. Strengthened parser-surface validation to reject drift in accepted tokens and lookup-table surfaces, including same-canonical alias additions or substitutions.
   - Demo-path mapping: open and patch-review, because `bootstrap` and `diff-preview` aliases are now guarded against silent parser-surface changes.
3. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
   - Demo-path mapping: retrieve/basket and patch-review, because smoke-route order stays deterministic for the current engine-first loop.
4. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and full parser-surface drift rejection.
   - Demo-path mapping: all command-backed demo steps, because tests cover the parser surface used to reach project-open, retrieval, patch-review, and export-handoff.
5. Included branch-tip non-metadata changes in this packet, including `scripts/scope-check.sh`, so the review basis matches the actual changed files.
   - Demo-path mapping: workflow governance, because review/integration can now validate the real branch contents before the command lane advances.

## Canonical Demo-Path Step Made More Real

- The CLI-first route from project open -> retrieval/basket -> patch review -> export handoff is more real because the parser contract now rejects silent drift in the tokens and lookup table that reach those steps.

## Files Changed

### Reviewed Implementation / Tooling Files

- `src/qual/commands/catalog.py` - lane-owned command contract implementation.
- `tests/unit/test_commands_catalog.py` - approved shared test coverage for command contract drift.
- `scripts/scope-check.sh` - shared tooling change included in this review basis.

### Metadata-Only Handoff Files

- `THREAD.md` - metadata-only packet pointer.
- `THREAD_PACKET.md` - canonical metadata-only handoff packet.

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Shared-by-approval implementation/test edits: `tests/unit/test_commands_catalog.py` under the approved shared-test exception.
- Shared tooling edits: `scripts/scope-check.sh`, explicitly included for review and justified above.
- Integrator-locked edits: none.
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`.
- Shared/integrator-locked edits: `YES` for the approved shared test and shared tooling file; no integrator-locked files are edited.

## Required Fixes Addressed From Reviewer Packet `20260429T033837Z`

1. Regenerated this handoff packet with an accurate implementation range and files changed list.
2. Included all non-metadata branch-tip changes in the review packet with ownership accounting and scope justification.
3. Strengthened `command_cli_contract()` to reject full parser-surface drift, with focused tests for same-canonical alias drift and missing expected CLI tokens.
4. Added explicit canonical demo-path mapping for each completed task and named the demo-path step made more real.
5. Re-ran and reported the required gates after establishing the corrected implementation basis.

## Commands Run + Outcomes

- `make scope-check`: PASS for branch `codex/feat-commands`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran smoke tests and 152 unit tests.
- `./typecheck-test.sh`: PASS; compiled Python sources in `src/`.
- `make ci`: PASS; ran scope-check, format, lint, compileall/typecheck, and full quality tests.

## Risks / Blockers

- Risk: `HIGH`.
- Blockers: none.

## Required Handoff Fields

### Branch Name

- `codex/feat-commands`

### Roadmap Item(s) Affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision Capability Affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing / Provider Impact Note

- None. This change only affects local command contract validation, command-catalog test coverage, and scope-check handoff enforcement metadata.
