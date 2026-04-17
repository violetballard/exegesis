# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `metadata-only reviewer-fix gate rerun refresh after 2026-04-17T05:15:20Z verification`
- Packet refresh role: `feature-fixer verification refresh after reviewer required fixes`

## Packet Traceability Note

- The command-catalog implementation under review remains
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- The reviewer-required parser-surface validation and token-drift regression
  coverage are already present on this branch.
- This packet refresh is metadata-only. It does not change the reviewed
  implementation; it records the latest fixer verification pass and required
  gate rerun.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any
  Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays
  deterministic, uses the canonical command order, and fails fast if the parser
  surface drifts from the catalog.

## Canonical Demo-Path Step Advanced

- Exact canonical demo-path step advanced: `open project/document`.
- Concrete blocker removed: while the CLI remains the active operator surface
  in Milestone 3, `command_cli_contract()` now rejects parser/catalog drift
  instead of allowing the active `open project/document` command surface to
  change silently.
- Scope boundary: this slice remains command-catalog hardening for the existing
  CLI contract. It does not add new commands, new flags, handler logic, or
  alternate workflow paths.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition of Done for This Lane

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it
  compares CLI canonical names against `command_names()` and raises
  `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by
  reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order alignment and drift rejection.
- Refreshed the handoff packet so it explicitly names the canonical
  `open project/document` demo-path step advanced by this CLI-contract slice.
- Re-ran the required scope, quality, typecheck, and CI gates after the
  reviewer-fix branch state was verified.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one
  focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so it explicitly states the exact canonical demo-path step advanced: `open project/document`.
5. Re-ran the full required gate sequence on the verified reviewer-fix branch state and refreshed the handoff metadata with that result.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Verification timestamp: `2026-04-17T05:15:20Z`

## Risks / Blockers

- Risk: low. Future intentional CLI parser changes still need matching catalog
  and test updates or the contract check will fail fast by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands by keeping the command-catalog contract
  deterministic and drift-resistant for the active `open project/document`
  operator path while Textual remains disabled.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable for
  `open project/document` while the command-catalog surface rejects parser
  drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface now fails loudly on
  catalog/parser drift, making the operator-facing contract explicit and
  traceable.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  and the only non-owned implementation path is the approved shared test
  `tests/unit/test_commands_catalog.py`.
