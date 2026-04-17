# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `metadata-only reviewer-fix finalization`
- Packet refresh role: `reviewer-fix handoff refresh`

## Packet Traceability Note

- The current branch tip includes later metadata-only packet refreshes. Review
  the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  and treat later packet-refresh commits as handoff alignment only unless a new
  runtime handoff is explicitly regenerated.

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

- Exact canonical demo-path step advanced: the CLI-first command route for
  `open project/document -> retrieve relevant material -> preview and apply or
  reject a patch -> export handoff`.
- Concrete blocker removed: the CLI-first operator path now rejects parser /
  catalog drift before the canonical command surface can silently reorder,
  drop, or desynchronize the command names that anchor that route slice of the
  engine-first MVP loop while Textual remains disabled.
- Scope boundary: this remains command-catalog contract hardening only. It does
  not add new commands, new flags, handler logic, or alternate workflow paths.

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
- Reissued the handoff packet as a command-catalog-only slice so the review
  scope matches the claimed implementation files and approval basis.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one
  focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval artifact: the reviewer packet supplied to this fixer pass is the
  source of truth for the exception and explicitly records `Approved shared-test
  exception for tests/unit/test_commands_catalog.py` for this command-catalog
  slice.
- Approval basis: `scripts/scope-check.sh` is the active branch enforcement in
  this worktree, and its `codex/feat-commands*` allowlist explicitly permits
  `tests/unit/test_commands_catalog.py` as the one approved shared test path.
  This handoff uses only that allowlisted shared test and claims no other
  non-owned implementation files.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap and vision labels.

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

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands by keeping the command-catalog contract
  deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command-catalog surface rejects parser drift before it can silently change
  the CLI operator contract for the current engine-first MVP loop.
- Writing-centered workflow - this is limited to keeping the active CLI entry
  surface deterministic for the current operator path; it does not add new
  engine workflow behavior.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  and the only non-owned implementation path is the approved shared test
  `tests/unit/test_commands_catalog.py`.
- Approval basis detail: the shared-file exception is limited to that one test
  path recorded in the reviewer packet supplied to this fixer pass and
  allowlisted under `codex/feat-commands*` in `scripts/scope-check.sh`. No
  integrator-locked runtime files are part of this reviewed implementation
  slice.
