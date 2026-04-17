# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `19ab31af48134d155c1eb782bd0ba95a5c25a268`
- Packet refresh role: `feature-fixer reviewer-required handoff refresh`

## Packet Traceability Note

- Review the command-catalog implementation at
  `19ab31af48134d155c1eb782bd0ba95a5c25a268`.
- This refresh is metadata-only and exists to satisfy the reviewer's required
  handoff fixes without changing the reviewed runtime implementation slice.
- Final feature-fixer refresh on `2026-04-17`: this post-review metadata
  update records that reviewer required fixes `1` and `2` are closed in the
  handoff itself and that a fresh full-gate pass was rerun before this commit.

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
  deterministic, uses the canonical command order, and fails fast if the
  parser surface drifts from the catalog-backed command specs.

## Canonical Demo-Path Step Advanced

- Required by `AGENTS.md`: this handoff explicitly states which canonical
  demo-path step the change makes more real.
- This slice strengthens the CLI-first operator surface for the current MVP
  loop, specifically the `project-open`, `retrieval`, `patch-review`, and
  `export-handoff` steps while Textual remains disabled.
- Concrete blocker removed: parser/catalog drift could silently reorder,
  replace, or drop accepted CLI entrypoints for those steps; the contract now
  fails fast instead.

## Scope Boundary

- This slice is command-catalog contract hardening only.
- It does not add new commands, new flags, handler logic, or alternate
  workflow paths.
- It preserves the existing MVP command surface rather than expanding it.

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
- Kept the returned CLI contract aligned with the canonical command order by
  returning the validated canonical names tuple directly.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order alignment and drift rejection.
- Refreshed the handoff packet so the reviewer-required demo-path mapping and
  contract-only scope boundary are explicit in the handoff itself.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one lane-owned command file plus
  one approved shared test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval basis: the reviewer packet supplied to this fixer pass is the
  source of truth for that one non-owned test path.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the
   validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for
   canonical-order alignment and drift rejection.
4. Updated the handoff packet so it explicitly names the canonical demo-path
   steps advanced and keeps the scope statement limited to contract hardening.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`
- `THREAD.md`

## Commands Run and Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Risk: `LOW`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command-catalog surface rejects parser drift before it can silently change
  the current operator contract.

### Explicit canonical demo-path step advanced

- The CLI-first `project-open`, `retrieval`, `patch-review`, and
  `export-handoff` steps are now more deterministic and smoke-testable because
  parser/catalog drift fails fast.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES` via one approved shared test only.
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  and the only non-owned implementation path is the approved shared test
  `tests/unit/test_commands_catalog.py`.
