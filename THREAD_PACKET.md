# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Packet refresh role: `feature-fixer reviewer-required traceability refresh`
- Packet refresh date: `2026-04-17`

## Packet Traceability Note

- This handoff is for the actual current `codex/feat-commands` branch tip.
- The earlier `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` packet basis is superseded
  for re-review because the branch contains additional non-metadata command-lane
  commits after that point.
- The implementation commit immediately below this metadata refresh was
  `c519ac9d8de567f905c2a69ce76bf4fdfdab3657`.
- Re-review should use the current branch tip as the merge candidate, not the
  older `f8d860ed...` slice.
- Relative to `codex/quality-baseline`, the reviewed branch-tip surface in this
  handoff is:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`

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

- Keep the CLI compatibility surface deterministic for the engine-first MVP
  loop while Textual remains disabled.
- Fail fast when the parser surface drifts away from the canonical
  command catalog instead of silently changing operator-visible behavior.

## Canonical Demo-Path Step Advanced

- Step advanced: `open project/document`.
- Concrete tie-back: the branch keeps the `bootstrap`-driven entry contract for
  `open project/document` deterministic, so the CLI cannot silently drift away
  from the canonical catalog while it remains the active operator surface.

## Scope Completed

1. Hardened the command catalog and CLI contracts in
   `src/qual/commands/catalog.py` so canonical names, parser tokens, route
   summaries, and workflow/demo contracts stay deterministic and reject drift.
2. Kept the compatibility exports and helper resolution under
   `src/qual/commands/__init__.py` and `src/qual/commands/canonical.py`
   aligned with the canonical command surface used by the MVP loop.
3. Tightened command-entry compatibility behavior in
   `src/qual/commands/diff_preview.py` and the related command-surface helpers
   so existing command entrypoints stay smoke-testable.
4. Added and updated focused regression coverage in
   `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`
   for parser-surface stability, canonical ordering, and command compatibility
   behavior.
5. Regenerated `THREAD.md` and `THREAD_PACKET.md` so the handoff now matches
   the real branch-tip merge candidate and explicitly names the demo-path step
   advanced.

## Scope Boundary

- This handoff is for the real branch-tip `feat-commands` surface listed above.
- It stays within Milestone 3 command-surface compatibility work.
- It does not add Textual UI work, routing/provider changes, or engine business
  logic outside the command compatibility layer.

## Files Changed

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`
- `THREAD.md`
- `THREAD_PACKET.md`

## Shared / Approval Note

- Shared-by-approval edits are present in this branch-tip handoff:
  `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
- This feature-fixer pass did not broaden that shared-file surface; it only
  refreshes the packet so the reviewer sees the real merge candidate.

## Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `MEDIUM`
- Remaining risk: the branch-tip command surface is broader than the original
  `f8d860ed...` slice, so re-review should evaluate the full listed surface
  rather than the earlier narrow packet basis.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the
  package/layout migration lands.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the
  engine-first MVP loop.

### Vision capability affected

- Canonical engine contract - the CLI compatibility layer keeps one stable
  command surface while the future Textual client remains disabled.
- Writing-centered workflow - the `open project/document` entry step stays
  deterministic and smoke-testable instead of depending on parser drift.
- Auditable state and workflow - command-surface drift fails explicitly instead
  of changing the operator contract silently.

### Routing/provider impact note

- None. This lane touches local command compatibility contracts and tests only.
