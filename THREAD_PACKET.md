# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `5fb0987e61321af1f10054771d075440bb86a203`
- Packet refresh role: `reviewer-required demo-path mapping refresh`

## Packet Traceability Note

- The implementation commit above applies the reviewer-required parser-surface fixes.
- The current branch tip is a docs-only handoff refresh that keeps this packet aligned with that reviewed implementation unless this handoff is regenerated.

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

- Single canonical demo-path step advanced: `continue working without losing context`.
- Why this exact step: this change does not add a new workflow action; it hardens the stable CLI operator surface that lets the current MVP loop continue safely after commands are wired, by making command dispatch deterministic and drift-failing instead of silently diverging from the catalog.
- AGENTS alignment statement: this slice makes `continue working without losing context` more real by ensuring the command-catalog contract stays explicit, ordered, and smoke-testable, so the CLI fallback surface remains dependable while Textual stays disabled.
- Scope-tightening note: this is command-contract hardening for the CLI-first MVP loop only. It does not claim broader workflow, retrieval, audit, or UI capability expansion.
- Reviewer fix note: this section exists specifically to satisfy the requested re-review correction to name the canonical demo-path step advanced by the handoff.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default catalog validates the full parser surface against the declared command entrypoints and raises `ValueError` when accepted CLI tokens drift from the catalog, which keeps the CLI fallback trustworthy for the `continue working without losing context` step of the canonical MVP loop.
- Kept the returned contract aligned with the canonical command order while treating parser-surface drift as a contract error instead of silently accepting alias substitutions or extra entrypoints, which keeps the `continue working without losing context` operator surface deterministic instead of silently changing underneath the user.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment, alias-substitution rejection, and extra accepted-entrypoint drift rejection, which makes the `continue working without losing context` CLI contract smoke-testable and auditable.
- Reissued the handoff packet as a command-catalog-only slice so the review scope matches the claimed implementation files and approval basis.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits. The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify the full default parser surface against the catalog and fail fast on alias substitution or extra-entrypoint drift.
   Demo-path step: `continue working without losing context`, because the CLI fallback must reject silent parser drift before an operator keeps using the next command in the loop.
2. Preserved canonical command ordering in the CLI contract while keeping parser-surface validation explicit.
   Demo-path step: `continue working without losing context`, because the active CLI surface must stay deterministic from run to run while the operator continues the workflow.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment plus alias-substitution and extra accepted-entrypoint parser-surface drift rejection.
   Demo-path step: `continue working without losing context`, because the smoke tests now prove the CLI contract used for continued work remains explicit and stable.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap and vision labels.
   Demo-path step: `continue working without losing context`, because the handoff now states exactly which canonical loop step this narrow contract-hardening slice protects.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff files

- `THREAD_PACKET.md`

## Commands Run and Outcomes

- `python -m unittest tests.unit.test_commands_catalog`: PASS
- `SCOPE_ALLOW_SHARED=1 make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Verification Note

- Re-verified on the current `codex/feat-commands` branch tip that the reviewer-required fixes are present in the implementation: `command_cli_contract()` now rejects full parser-surface drift for the default catalog, and `tests/unit/test_commands_catalog.py` covers alias-substitution and extra-entrypoint drift where canonical command order alone would still match.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant, which removes a concrete blocker from the `continue working without losing context` demo-path step: the operator-facing CLI surface can no longer silently drift underneath a live workflow.
- feat-commands - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the stable CLI fallback needed to keep the current demo path usable after each command invocation.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract that the user relies on to continue working without losing context.
- Auditable state and workflow - the command surface now fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable at the exact point where a continued workflow session would otherwise become ambiguous.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: lane-owned runtime edits stay in `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
- Exact approved scope-check invocation: `SCOPE_ALLOW_SHARED=1 make scope-check`
- Approval basis: `THREAD_OWNERSHIP.md` lists `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and the handoff keeps that exception limited to this one test file.
- Scope-tightening confirmation: no additional shared or integrator-locked implementation files are part of this reviewed slice.
