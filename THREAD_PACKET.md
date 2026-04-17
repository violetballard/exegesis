# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `6eafb0daef3f501ac5f59ac285d0d364f6b5b48e`
- Packet refresh commit: `this metadata-only feature-fixer refresh commit on codex/feat-commands`
- Packet refresh role: `feature-fixer required-fixes packet retargeting`

## Packet Traceability Note

- Earlier packet revisions incorrectly anchored review scope to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` even though later branch commits changed implementation files.
- The actual implementation review target is the current pre-refresh branch tip `6eafb0daef3f501ac5f59ac285d0d364f6b5b48e`.
- This follow-up refresh is metadata only. It does not change the reviewed implementation; it corrects packet traceability so the handoff matches the real branch state and review scope.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI-first command surface for the engine-first MVP loop so the canonical demo path keeps deterministic parser entrypoints, parser-ready shim rewrites, and stable smoke/demo routing while Textual remains disabled.

## Canonical Demo-Path Step Advanced

- Exact steps advanced:
  - `open project/document`
  - `retrieve relevant material`
  - `preview and apply or reject a patch`
  - `save and continue`
- AGENTS alignment: this branch strengthens the CLI-first operator surface for the canonical engine-side demo path while Textual remains disabled.
- Why these steps: the command catalog now models parser entrypoints, surface tokens, shim rewrites, smoke/demo invocation plans, and terminal compatibility aliases that cover the active MVP command route from bootstrap through retrieval, patch handling, and export/persist handoff.
- Scope boundary: this branch stays inside command-surface compatibility work. It does not embed new engine business logic in handlers or expand beyond command routing, command contracts, and focused diff-preview compatibility.

## Scope-Tightening Note

- This is not general CLI cleanup. It removes concrete CLI-contract blockers from the canonical demo path by making the command surface explicit, smoke-testable, and stable across parser tokens, route tokens, and compatibility aliases.

## Ready for Handoff

- This work now makes the canonical Milestone 3 CLI path more real because the command layer exposes deterministic demo/mvp route helpers, parser-ready alias normalization, and fail-fast contract validation for the command surface that operators actually use.
- Pre-handoff alignment statement: this is CLI compatibility and demo-path contract work for the active MVP loop, not standalone infra cleanup.

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

- Expanded the command catalog in `src/qual/commands/catalog.py` to expose deterministic CLI contracts, route contracts, shim contracts, smoke/demo invocation plans, and resolution helpers for the canonical demo-path command surface.
- Added parser-ready compatibility alias handling for retrieval, patch, persist, and export/terminal flows so surface tokens normalize back to stable CLI entrypoints without silently changing pinned terminal operation kinds.
- Updated the public command exports and focused diff-preview compatibility hooks in `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, and `src/qual/commands/diff_preview.py` so the broader command-surface helpers stay reachable and smoke-testable.
- Added comprehensive regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, then refreshed the handoff packet so the claimed scope, reviewed files, and demo-path alignment match the actual implementation tip.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: packeted as 4 meaningful task groups and limited to lane-owned command files plus approved shared tests.
- Runtime implementation stays within `src/qual/commands/**`; the only non-owned implementation paths are approved shared tests.

## Approved Exception Note

- Approved shared-test exceptions for:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`

## Tasks Completed

1. `open project/document`: locked the parser-facing command contract and demo-path command ordering to deterministic catalog data, including fail-fast drift detection and explicit primary entrypoints for the bootstrap route.
2. `retrieve relevant material`: made retrieval-facing command shims parser-ready so demo/mvp route helpers, surface tokens, and resolution helpers keep the retrieval step aligned with the canonical command catalog.
3. `preview and apply or reject a patch` and `save and continue`: normalized terminal/export/persist/apply/reject compatibility aliases into stable parser-ready argv while preserving pinned terminal operation kinds for demo-path routing.
4. `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `save and continue`: added focused regression coverage for the expanded command-surface helpers and refreshed the handoff packet so review scope and demo-path alignment are truthful.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`

## Commands Run and Outcomes

- Revalidation note: reran the required lane gates during this metadata-only feature-fixer refresh; all remained green.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: medium. The command surface is now much more explicit and better covered, but it also centralizes more shim and demo-path routing behavior in the catalog. Future intentional CLI changes still need matching catalog, shim, and regression-test updates or they will fail fast.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the canonical demo-path command surface deterministic, parser-ready, and smoke-testable.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, including bootstrap, retrieval, diff-preview, and terminal/export compatibility routing.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable because parser drift, route drift, and shim drift now fail fast instead of silently changing the operator-facing command surface.
- Auditable state and workflow - the command catalog now makes the active demo-path routing and terminal handoff aliases explicit enough to smoke-test and trace.

### Routing/provider impact note

- None. This branch only affects local command-surface contracts, parser-ready alias normalization, and focused command compatibility coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`, and the only non-owned implementation paths are the approved shared tests `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
