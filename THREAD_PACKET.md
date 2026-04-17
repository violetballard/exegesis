# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `36a360a9464d2f08f55129bc70e1aafe4574721b`
- Packet refresh commit: `36a360a9464d2f08f55129bc70e1aafe4574721b`
- Packet refresh role: `reviewer-fix plan-alignment refresh`

## Packet Traceability Note

- The original reviewer packet pointed at
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, but this branch now contains the
  required command-catalog fixes for parser-surface drift rejection and the
  later demo-surface follow-up through branch tip
  `36a360a9464d2f08f55129bc70e1aafe4574721b`. Treat later packet-only commits
  after that implementation tip as handoff alignment unless a new runtime
  handoff is explicitly regenerated.

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
  deterministic, preserves the declared parser-entrypoint order per command,
  and fails fast if the accepted CLI surface drifts from the catalog-backed
  command specs.

## Canonical Demo-Path Step Advanced

- AGENTS.md canonical demo-path step advanced: `open project/document ->
  retrieve relevant material -> preview and apply or reject a patch -> save and
  continue working without losing context`, specifically the CLI-first command
  route slice that covers `open project/document -> retrieve relevant material
  -> preview and apply or reject a patch -> export handoff`.
- Concrete blocker removed on that step: the CLI-first operator path now
  rejects parser / catalog drift before accepted command entrypoints can
  silently reorder, substitute aliases, drop expected tokens, or add extra
  entrypoints that would desynchronize that route slice of the engine-first MVP
  loop while Textual remains disabled.
- Why this is not second-order work: Milestone 3 currently depends on the CLI
  remaining the active operator surface. If the parser surface drifts silently,
  the engine-first demo path can stop being reliably smoke-testable even when
  engine behavior is unchanged, which makes this command-catalog guardrail a
  direct stability requirement for the current loop rather than speculative UX
  work.
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
  validates the full parser surface against the declared per-command CLI
  entrypoints, not just the deduplicated canonical-name projection, and raises
  `ValueError` when the accepted CLI surface drifts.
- Kept the returned CLI contract deterministic by preserving canonical command
  order for CLI-exposed specs while also enforcing the declared entrypoint
  order and lookup table shape for the default parser surface.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for parser-surface drift cases, including missing primary tokens, alias
  substitution, removed expected aliases, reordered entrypoints, and extra
  accepted entrypoints.

## Metadata-Only Handoff Maintenance

- Refreshed the handoff packet so the review scope points at the current
  command-catalog implementation commit and the actual parser-surface invariant
  enforced in this branch.

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

1. Hardened `command_cli_contract()` so the CLI route slice for `open project/document -> retrieve relevant material -> preview and apply or reject a patch -> export handoff` fails fast when accepted parser tokens drift from the command catalog.
2. Preserved deterministic CLI contract ordering for that same CLI-first demo-path slice by keeping canonical command order and declared per-command entrypoint order aligned with the catalog-backed parser surface.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for parser-surface drift on that CLI-first demo-path slice, including alias substitution, alias removal, entrypoint reordering, and extra accepted entrypoints.

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
- Scope limit note: this slice does not claim workflow, persisted-state, or
  auditability changes. It is limited to deterministic CLI compatibility for
  the active engine-first operator surface while Textual remains disabled.

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
