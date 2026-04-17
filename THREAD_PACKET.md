# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `e2e1c437b81b8b39cd266ccd369d21774e2c8777`
- Packet refresh role: `feature-fixer reviewer-required handoff refresh`

## Packet Traceability Note

- Review the true branch-tip implementation at
  `e2e1c437b81b8b39cd266ccd369d21774e2c8777`.
- The previous approved review baseline for this re-review is
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  (`feat(commands): lock CLI contract to command catalog`).
- The reviewed runtime commit set for this handoff is:
  - `19ab31af48134d155c1eb782bd0ba95a5c25a268`
    (`feat(commands): expose demo loop contract helpers`)
  - `3a407703933a0d127c78864e3ec91458aad50b20`
    (`feat(commands): add demo-path compatibility shims`)
  - `e2e1c437b81b8b39cd266ccd369d21774e2c8777`
    (`Add demo command compatibility contract`)
- The reviewed implementation delta for this handoff is the real branch-tip
  range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..e2e1c437b81b8b39cd266ccd369d21774e2c8777`.
- This packet refresh updates handoff metadata only; it does not change the
  reviewed implementation range above.
- Full required gates were rerun against the current branch tip after this
  packet refresh.

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

- Keep the Milestone 3 CLI command surface deterministic and migration-safe by
  exposing canonical demo-loop helpers and parser-ready compatibility shims for
  the current engine-first MVP flow.

## Canonical Demo-Path Step Advanced

- AGENTS-required explicit step statement: this change makes the canonical
  demo-path steps `open project/document`, `retrieve relevant material`,
  `preview and apply or reject a patch`, and `continue working without losing
  context` more real for the CLI-first MVP loop.
- Concrete blocker removed: older demo-path verbs such as `open-project`,
  `review`, `save`, `apply`, and `reject` now normalize to the canonical
  parser-facing command surface instead of depending on callers to know the
  internal command tokens.
- Demo-path impact: operator-facing demo-loop commands are more reliable and
  smoke-testable because catalog/parser drift is rejected before those CLI
  steps can silently diverge.

## Scope Boundary

- This slice stays in `feat-commands` Milestone 3 CLI compatibility work.
- It adds command-catalog helpers and compatibility shims only.
- It does not add new engine business logic, new provider behavior, or new UI
  work.

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

- Extended the reviewed command-catalog implementation range from
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` to the true branch tip
  `e2e1c437b81b8b39cd266ccd369d21774e2c8777` so the handoff matches the code
  actually on `codex/feat-commands`.
- Exposed canonical demo-loop helpers in `src/qual/commands/catalog.py` and
  `src/qual/commands/__init__.py` so the MVP loop now has catalog, token,
  lookup-table, invocation-plan, and compatibility-contract accessors for
  `open project/document`, `retrieve relevant material`, and `preview and
  apply or reject a patch`.
- Added demo-path compatibility-token normalization for older surface verbs so
  `command_demo_*`, `command_mvp_*`, and the demo compatibility contract
  resolve parser-ready argv through the canonical command catalog and keep
  `continue working without losing context` stable across older CLI spellings.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py`
  and `tests/unit/test_diff_preview.py` for the demo-loop helpers,
  compatibility shims, and demo command compatibility contract behavior.
- Refreshed the handoff packet so the reviewed commit set, files changed, gate
  evidence, and explicit canonical demo-path mapping match the actual branch
  history.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The runtime slice remains limited to one lane-owned command file plus one
  approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval basis: the reviewer packet supplied to this fixer pass is the
  source of truth for that one non-owned test path.

## Tasks Completed

1. Added canonical demo-loop helper accessors for the Milestone 3 CLI command
   surface.
2. Added compatibility-token normalization so older demo-path verbs map to the
   canonical parser-facing command surface.
3. Added a demo command compatibility contract export surface in
   `src/qual/commands/__init__.py` plus its backing catalog support.
4. Added focused regression coverage for the demo-loop helpers, compatibility
   shims, and diff-preview compatibility behavior in
   `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
5. Regenerated the handoff packet so it truthfully reports the reviewed commit
   range, scope, files changed, and gate evidence.

## Files Changed

### Reviewed implementation files in `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..e2e1c437b81b8b39cd266ccd369d21774e2c8777`

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`
- `THREAD.md`

## Commands Run and Outcomes

- `make scope-check`: PASS on current branch tip after packet refresh
- `./quality-format.sh --check`: PASS on current branch tip after packet refresh
- `./quality-lint.sh`: PASS on current branch tip after packet refresh
- `./quality-test.sh`: PASS on current branch tip after packet refresh
- `./typecheck-test.sh`: PASS on current branch tip after packet refresh
- `make ci`: PASS on current branch tip after packet refresh

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
  command catalog exposes canonical demo-loop helpers and normalizes older
  surface verbs to the parser-facing contract.

### Routing/provider impact note

- None. This change only affects local command-catalog helpers, parser-surface
  normalization, and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared-by-approval edits: `YES` via the approved shared test path
  `tests/unit/test_commands_catalog.py`.
- Integrator-locked edits: `NO`.
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  and this fixer refresh changes only handoff metadata in `THREAD_PACKET.md`;
  it does not add any new non-owned implementation edits beyond the approved
  shared test path above.
