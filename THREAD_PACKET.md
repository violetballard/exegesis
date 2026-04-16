# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix metadata refresh`

## Packet Traceability Note

- Keep the approval basis pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- This packet refresh is metadata-only and exists to satisfy the reviewer's required fixes without changing the reviewed implementation scope.
- Preserve the approved shared-test exception note for `tests/unit/test_commands_catalog.py`.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Canonical Demo-Path Mapping

- Explicit canonical demo-path step advanced: `open project/document`.
- This change makes the `open project/document` step more real by keeping the operator-facing CLI command contract deterministic, preserving canonical command ordering, and rejecting parser/catalog drift before the entry command surface can silently change.
- Wording anchor: this packet uses the exact canonical demo-path step text required by `AGENTS.md` and `ROADMAP.md`, rather than only broad Milestone 3 labels.
- Secondary effect: the same deterministic contract helps the existing CLI fallback remain smoke-testable for downstream loop steps, including `preview/apply or reject a patch`, while Textual stays disabled.
- Concrete blocker removed: Milestone 3 depends on a stable CLI-first command surface while the package/layout migration lands, and this slice removes the risk that parser entrypoints drift away from the catalog without failing fast at contract construction time.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Regenerated the handoff packet as a metadata-only refresh so the review scope stays pinned to the command-catalog implementation commit and includes the explicit demo-path mapping requested in review.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
4. Refreshed the handoff packet so the review remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, includes the explicit `open project/document` demo-path mapping, and keeps the shared-test exception note intact.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Risk: `LOW`
- Residual risk rationale: this is a metadata-only packet refresh over an already-reviewed two-file contract-hardening diff with no routing/provider changes and no remaining known blockers after the required gate suite.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - this change strengthens the requirement that the CLI can still execute the MVP loop while Textual remains disabled by keeping the command-catalog contract deterministic and drift-resistant for the current `open project/document` entry step.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- Plan-alignment note: this is a contract-hardening slice, not a UX expansion; it directly removes a concrete blocker on the canonical demo path by making the `open project/document` CLI entry surface auditable and deterministic for smoke tests during the engine-first loop.

### Vision capability affected

- `Canonical engine contract` - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- `Auditable state and workflow` - the command surface now fails loudly on catalog/parser drift, so operator-facing command behavior is explicit and traceable instead of silently diverging.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.
