# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `this metadata-only feature-fixer refresh commit on codex/feat-commands`
- Packet refresh role: `feature-fixer required-fixes packet retargeting`

## Packet Traceability Note

- The implementation review target remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Later packet-refresh commits on this branch are metadata only unless a new implementation packet is explicitly regenerated.
- This follow-up refresh is metadata only. It does not change the reviewed implementation; it tightens the handoff text so the reviewer-required demo-path mapping and scope boundary are explicit for the command-catalog slice.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the existing CLI command contract for the engine-first MVP loop so `command_cli_contract()` stays deterministic, preserves canonical command order, and fails fast if the parser surface drifts from the catalog while Textual remains disabled.

## Canonical Demo-Path Step Advanced

- Exact CLI-first MVP steps strengthened:
  - `open project/document`
  - `retrieve relevant material`
  - `preview and apply or reject a patch`
- AGENTS alignment: this slice makes those existing CLI demo-path steps more reliable by keeping the parser-facing command list locked to the canonical catalog order instead of allowing silent drift.
- Concrete blocker removed: before this change, parser entrypoints could diverge from the catalog and still produce a plausible-looking CLI contract. This change removes that blocker by requiring the parser-derived canonical names to match `command_names()` exactly and by failing fast when they do not.
- Scope boundary: this slice is limited to command-catalog contract validation and its focused regression coverage. It does not add new commands, add new flags, widen the MVP loop, or embed engine behavior in handlers.

## Scope-Tightening Note

- This is not general CLI cleanup. It is a narrow command-catalog hardening change for the existing MVP command loop.
- This is a contract-only `feat-commands` slice for Milestone 3 CLI compatibility while Textual remains disabled.
- It does not add new commands, flags, or handler logic. It only makes the existing command contract deterministic and drift-resistant.

## Ready for Handoff

- This work now makes the canonical Milestone 3 CLI path more real because the catalog rejects parser drift before it can silently alter the operator-facing command route for open, retrieval, and patch-review steps.
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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares parser-derived canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Preserved canonical command ordering in the returned CLI contract by reusing the validated canonical tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Refreshed the handoff packet so the claimed review scope, demo-path mapping, and scope boundary match this command-catalog-only slice.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap and remained limited to one lane-owned command file plus one approved shared test file.
- Runtime implementation stays within `src/qual/commands/**`; the only non-owned implementation path is the approved shared test.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks Completed

1. `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch`: locked the parser-facing CLI contract to deterministic catalog data so those existing steps keep the canonical command order instead of drifting silently.
2. Hardened `command_cli_contract()` to fail fast when parser-derived canonical names diverge from `command_names()`.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Refreshed the handoff packet so the review scope explicitly stays limited to command-catalog determinism and does not claim new commands, flags, or handler logic.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

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

- Residual risk: low. Future intentional CLI parser changes still need matching catalog and regression-test updates or `command_cli_contract()` will fail fast by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the existing CLI route for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` deterministic while Textual remains disabled.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the current engine-first MVP loop, specifically by preventing parser/catalog drift in the existing bootstrap, retrieval/context, and diff-preview command surface.

### Vision capability affected

- Canonical engine contract - the operator-facing CLI contract for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` now fails fast when parser drift would otherwise silently change the command surface.
- Auditable state and workflow - the catalog/parser consistency check makes that existing CLI contract explicit and traceable instead of depending on implicit ordering assumptions.

### Routing/provider impact note

- None. This branch only affects local command-catalog validation and focused regression coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
