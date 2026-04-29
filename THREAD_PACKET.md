# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: this metadata-only fixer commit
- Packet refresh role: metadata-only reviewer-fix finalization for reviewer packet `20260429T010138Z`

## Packet Traceability Note

- Review the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Later packet-refresh commits are metadata-only for this review unless they modify `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py`.
- This fixer pass does not change command implementation or tests.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.

## Canonical Demo-Path Step Advanced

- This makes the open/retrieve/basket/patch-review CLI smoke path more real by keeping the parser-visible command contract deterministic and failing fast when parser tokens drift from the command catalog.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and lane size limits.
- The reviewed implementation slice stays limited to one owned command file plus one focused approved shared-by-approval test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Shared-by-approval edits: YES, `tests/unit/test_commands_catalog.py` under approved exception.
- Integrator-locked edits: NO.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice, names the canonical demo-path step advanced, and uses corrected ownership accounting.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run + Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS (144 tests)
- `./typecheck-test.sh`: PASS
- `make ci`: PASS (includes scope-check, format, lint, compile/typecheck, and quality-test)

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none.

## Required Handoff Fields

### Branch Name

- `codex/feat-commands`

### Scope Completed

- Command-catalog contract validation now keeps CLI canonical names aligned with the canonical command order and rejects parser/catalog drift.

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

## Reviewer Packet `20260429T010138Z` Fix Satisfaction

1. Canonical demo-path step advanced: satisfied by stating that this makes the open/retrieve/basket/patch-review CLI smoke path more real through deterministic parser-visible command contract validation.
2. Ownership accounting: satisfied by distinguishing the approved shared-by-approval test edit from integrator-locked edits.
3. Reviewed implementation scope: kept fixed to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer pass changes metadata only.
