# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `HEAD (current branch tip including reviewer fixes)`
- Packet refresh commit: `HEAD (feature-fixer required-fix handoff refresh)`
- Packet refresh role: `feature-fixer reviewer-required-fix packet alignment`

## Packet Traceability Note

- The current review target is the actual branch tip
  `edff6d8f18ea4b8a24c87bbb062226d5fe6b1961`.
- This packet no longer treats later lane commits as metadata-only.
- Re-review should cover the command-catalog implementation now present at the
  branch tip, including the earlier `801532e089c1b123bb586c18ac1f874141ebfdd1`
  workflow compatibility invocation-table change and the current
  `edff6d8f18ea4b8a24c87bbb062226d5fe6b1961` compatibility-variant hardening.
- Latest packet refresh prepared after the required-fix rerun on
  `2026-04-17`.

## Reviewer-Required Fix Verification

- Required fix 1, true review target: satisfied by anchoring this packet to the
  real branch tip instead of the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  slice.
- Required fix 2, explicit plan alignment: satisfied by naming the exact
  canonical demo-path steps and the concrete CLI contract blocker removed.
- Required fix 3, shared-file approval provenance: satisfied by tracing the
  approved shared-test exception for `tests/unit/test_commands_catalog.py` to
  prior handoff commits `0576acdd`, `c252f4d3`, and `3edc503e`, which recorded
  the approval reference for this lane's command-catalog test coverage.
- Required fix 4, branch-tip validation evidence: satisfied by rerunning the
  full required gate suite against the current branch tip and recording the
  outcomes below.

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

- Keep the `feat-commands` CLI compatibility surface deterministic and
  smoke-testable for the active Milestone 3 engine-first MVP loop by
  hardening command-catalog contracts, workflow compatibility invocation
  tables, and compatibility-token normalization.

## Canonical Demo-Path Step Advanced

- Exact canonical demo-path steps advanced:
  `open project/document`,
  `retrieve relevant material`,
  `preview and apply or reject a patch`,
  and `continue working` into `export handoff`.
- Concrete blocker removed:
  the CLI compatibility layer can no longer silently diverge between command
  catalog order, workflow compatibility invocation argv, and accepted
  compatibility-token variants for those operator-facing steps.
- Step mapping:
  `bootstrap` keeps `open project/document` deterministic,
  `context-basket` keeps `retrieve relevant material` deterministic,
  `diff-preview` and its workflow compatibility variants keep
  `preview and apply or reject a patch` deterministic,
  and `terminal`/persist-export compatibility routes keep `continue working`
  and `export handoff` deterministic while Textual remains disabled.
- Scope-tightening note:
  this packet claims only CLI contract hardening for existing MVP-loop
  entrypoints; it does not claim new workflow behavior or new command
  semantics.

## Scope Boundary

- This slice stays in `feat-commands` Milestone 3 CLI compatibility work.
- It hardens command-catalog validation, workflow compatibility invocation
  data, and compatibility-token normalization.
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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the
  parser-facing CLI contract validates canonical command order against
  `command_names()` and fails fast on drift.
- Added workflow compatibility invocation-table fields and exported helpers in
  `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py` so the
  current MVP workflow compatibility surface exposes parser-ready argv data
  alongside lookup data.
- Hardened demo compatibility-token normalization and transition lookup in
  `src/qual/commands/catalog.py` so accepted compatibility variants resolve to
  the canonical demo workflow tokens instead of silently missing transition
  edges.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  for canonical-order drift rejection, workflow compatibility invocation-table
  behavior, and demo compatibility transition resolution.
- Refreshed the handoff packet to align review scope, demo-path mapping,
  approval provenance, and gate evidence to the actual branch tip.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and lane size limits for this narrow command-catalog slice.
- Runtime edits remain in lane-owned `src/qual/commands/**`.
- The only non-owned implementation path remains the approved shared test file
  `tests/unit/test_commands_catalog.py`.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval provenance:
  `THREAD_OWNERSHIP.md` marks that file as `Shared by approval only`, and the
  lane previously recorded the approval trace in handoff commits `0576acdd`,
  `c252f4d3`, and `3edc503e`.
- This packet carries forward that same shared-test approval for the current
  command-catalog review scope; no additional shared or integrator-locked
  implementation paths are claimed.

## Tasks Completed

1. Hardened `command_cli_contract()` to reject canonical-name drift and keep
   canonical order deterministic.
2. Added workflow compatibility invocation-table data and exports for the
   current MVP workflow compatibility surface.
3. Hardened compatibility-token variant normalization so demo workflow
   transition lookups resolve accepted compatibility verbs to canonical tokens.
4. Added or retained focused regression coverage in
   `tests/unit/test_commands_catalog.py` for the branch-tip command-catalog
   behavior under review.
5. Refreshed the handoff packet so re-review targets the actual branch tip and
   includes explicit demo-path and approval-trace evidence.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification timestamp: `2026-04-17T14:47:31Z`

## Risks / Blockers

- Risk: `LOW`
- Remaining risk: future command-surface additions still need matching
  regression coverage anywhere parser-facing compatibility tokens or workflow
  invocation tables expand.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands by keeping the CLI command surface
  deterministic for the active MVP loop while Textual remains disabled.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - the CLI compatibility surface stays stable and
  smoke-testable for the current engine-first MVP loop while Textual remains
  disabled.
- Auditable state and workflow - the command surface now fails loudly on drift
  and keeps compatibility-token routing explicit and traceable for operator
  flows.

### Routing/provider impact note

- None. This change only affects local command contract validation, command
  workflow compatibility data, and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay inside lane-owned
  `src/qual/commands/**`, and the only non-owned implementation path in scope
  is the approved shared test `tests/unit/test_commands_catalog.py`.
