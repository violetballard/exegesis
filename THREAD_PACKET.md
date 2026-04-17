# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `e2e1c437b81b8b39cd266ccd369d21774e2c8777`
- Packet refresh role: `feature-fixer reviewer-required verification refresh`

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

## Reviewer-Required Fix Verification

- Required fix 1 satisfied: `src/qual/commands/catalog.py` now validates the
  full parser compatibility surface through the command-spec-declared CLI
  entrypoints, not just canonical-name order, and raises
  `ValueError("Command CLI parser surface is inconsistent")` when the parser
  surface drifts.
- Required fix 2 satisfied: `tests/unit/test_commands_catalog.py` includes
  focused negative coverage for parser-surface drift that still preserves the
  canonical command order, including alias substitution, reordered accepted
  entrypoints, removed expected aliases, and extra accepted entrypoints.
- Required fix 3 satisfied: this packet explicitly names the canonical
  demo-path steps advanced and keeps the AGENTS-required step statement in the
  handoff.

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
  smoke-testable because parser/catalog drift is rejected before those CLI
  steps can silently reorder or desynchronize from the catalog.

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
- Revalidated the reviewer-requested parser-surface drift guard and regression
  coverage on the current branch tip, then refreshed this packet so the
  numbered required fixes are explicitly traceable in the handoff.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute
  budget, and the lane size limits.
- The runtime slice remains limited to one lane-owned command file plus one
  approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- Approval provenance: the user-supplied reviewer packet for this fixer pass
  is the governing source of truth, and its enclosed feature handoff records
  an approved shared-test exception for
  `tests/unit/test_commands_catalog.py`.
- Approval basis: `THREAD_OWNERSHIP.md` marks
  `tests/unit/test_commands_catalog.py` as `Shared by approval only` for the
  `codex/feat-commands*` lane, and `scripts/scope-check.sh` explicitly allows
  that path for `codex/feat-commands*`.
- This metadata-only reissue preserves that previously approved shared-test
  path and does not add any new non-owned implementation edits.

## Tasks Completed

1. Made the canonical CLI `open project/document` step more real by exposing
   demo-loop helper accessors for the Milestone 3 command surface.
2. Made the canonical CLI `retrieve relevant material` and `preview and apply
   or reject a patch` steps more real by normalizing older demo-path verbs to
   the parser-facing canonical command surface.
3. Made the CLI `continue working without losing context` step more real by
   exporting a demo command compatibility contract from
   `src/qual/commands/__init__.py` with backing catalog support.
4. Kept the CLI-first MVP loop smoke-testable for those canonical steps by
   adding focused regression coverage for the demo-loop helpers,
   compatibility shims, and diff-preview compatibility behavior in
   `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
5. Regenerated the handoff packet so it truthfully reports the reviewed commit
   range, scope, files changed, gate evidence, and AGENTS-required
   canonical demo-path mapping.

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

- `make scope-check`: PASS during feature-fixer verification on current branch tip
- `./quality-format.sh --check`: PASS during feature-fixer verification on current branch tip
- `./quality-lint.sh`: PASS during feature-fixer verification on current branch tip
- `./quality-test.sh`: PASS during feature-fixer verification on current branch tip
- `./typecheck-test.sh`: PASS during feature-fixer verification on current branch tip
- `make ci`: PASS during feature-fixer verification on current branch tip

## Risks / Blockers

- Risk: `LOW`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands so the engine-first demo path can still
  execute `open project/document`, `retrieve relevant material`, `preview and
  apply or reject a patch`, and continue through the current CLI surface.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop, specifically the canonical CLI-first demo path while
  Textual remains disabled.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the
  command catalog exposes canonical demo-loop helpers and normalizes older
  surface verbs to the parser-facing contract.
- Writing-centered workflow - the CLI operator path for opening work,
  retrieving context, reviewing patches, and continuing the session remains
  deterministic and smoke-testable during the Milestone 3 migration.

### Routing/provider impact note

- None. This change only affects local command-catalog helpers, parser-surface
  normalization, and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared-by-approval edits: `YES` via the approved shared test path
  `tests/unit/test_commands_catalog.py`.
- Integrator-locked edits: `NO`.
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`,
  the only non-owned implementation path in the reviewed delta is the
  approved shared test `tests/unit/test_commands_catalog.py`, and this fixer
  refresh changes only handoff metadata in `THREAD_PACKET.md`; it does not
  add any new non-owned implementation edits beyond that approved path.
- Concrete approval citation: `THREAD_OWNERSHIP.md` lists
  `tests/unit/test_commands_catalog.py` under `Shared by approval only` for
  `codex/feat-commands*`, and `scripts/scope-check.sh` contains the matching
  lane-specific allowance for that shared test path.
