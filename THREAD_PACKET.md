# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: pending metadata-only fixer commit for reviewer packet `20260429T033347Z`
- Packet refresh role: metadata-only reviewer-fix finalization

## Packet Traceability Note

- Review the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Treat later packet-refresh commits as metadata-only unless a regenerated handoff names a newer implementation commit.
- This fixer pass does not add implementation changes, so the implementation review target remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Reviewer packet `20260429T033347Z` required handoff accounting fixes only.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.
- Corrected metadata-only file accounting for reviewer packet `20260429T033347Z` by listing both `THREAD.md` and `THREAD_PACKET.md`.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and lane size limits.
- The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap and vision labels.
5. Amended metadata accounting for reviewer packet `20260429T033347Z` so all packet-refresh files and ownership categories are explicit.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py` - lane-owned implementation file.
- `tests/unit/test_commands_catalog.py` - shared-by-approval test file with approved exception.

### Metadata-Only Handoff Files

- `THREAD.md` - metadata-only packet pointer changed in packet refresh commit `4baa9da1772c091cb911b707d9f4b5cbd8ee923f` and this fixer pass.
- `THREAD_PACKET.md` - canonical metadata-only handoff packet changed in packet refresh commit `4baa9da1772c091cb911b707d9f4b5cbd8ee923f` and this fixer pass.

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Shared-by-approval implementation/test edits: `tests/unit/test_commands_catalog.py` under the approved shared-test exception.
- Integrator-locked edits: none.
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`.
- Shared/integrator-locked edits: `YES` only because the approved shared-test exception touches `tests/unit/test_commands_catalog.py`; no integrator-locked files are edited.

## Required Fixes Addressed From Reviewer Packet `20260429T033347Z`

1. `THREAD.md` is now listed under metadata-only handoff files alongside `THREAD_PACKET.md`.
2. Ownership accounting now states exactly which changed files are lane-owned, shared-by-approval, integrator-locked, and metadata-only.
3. The implementation review target remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` because this fixer pass adds no implementation commit.

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

- None. This change only affects local command contract validation and focused command-catalog test coverage.
