# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `feature-fixer reviewer-required metadata refresh`

## Packet Traceability Note

- The current branch tip is a metadata-only fixer refresh.
- Review the command-catalog implementation at
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Treat later commits in this lane as metadata-only handoff refreshes for this
  re-review unless a new feature packet is explicitly generated.
- This packet refresh corrects the handoff metadata only; it does not broaden
  the reviewed implementation scope beyond the command-catalog slice above.

## Reviewer-Required Fix Verification

- Required fix 1 satisfied: this packet explicitly states which canonical
  demo-path steps this command-catalog change makes more real for the
  CLI-first MVP loop.
- Required fix 2 satisfied: the `Files changed` section now includes both
  metadata-only handoff files touched by the refresh flow,
  `THREAD_PACKET.md` and `THREAD.md`.
- Required fix 3 satisfied: the approval basis stays scoped to the reviewed
  implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and the
  narrow command-catalog work only.

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
  parser surface drifts from the catalog.

## Canonical Demo-Path Step Advanced

- AGENTS-required explicit step statement: this change makes the canonical
  CLI demo-path steps `open project/document`, `retrieve relevant material`,
  and `preview and apply or reject a patch` more reliable by keeping the
  parser-facing command surface deterministic and drift-resistant.
- Concrete blocker removed: parser/catalog drift can no longer silently
  reorder or desynchronize the operator-facing command contract for those
  CLI-first MVP steps.

## Scope Boundary

- This slice stays in `feat-commands` Milestone 3 CLI compatibility work.
- It only hardens command-catalog contract validation and focused regression
  coverage.
- It does not add new engine business logic, new command flags, or new UI
  behavior.

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
  approved shared test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency
   against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the
   validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for
   canonical-order alignment and drift rejection.
4. Regenerated the handoff packet so the branch metadata stays scoped to the
   command-catalog slice and uses the current roadmap and vision labels.

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
  package/layout migration lands by keeping the command-catalog contract
  deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command-catalog surface rejects parser drift before it can silently change
  the operator contract.
- Auditable state and workflow - the command surface now fails loudly on
  catalog/parser drift, making the operator-facing contract explicit and
  traceable.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused
  command-catalog test coverage.

## Scope-check / Ownership Note

- Shared-by-approval edits: `YES`.
- Integrator-locked edits: `NO`.
- Ownership detail: the only non-owned implementation path in this slice is
  the approved shared test `tests/unit/test_commands_catalog.py`.
