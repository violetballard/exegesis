# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `see final HEAD SHA from feature-fixer delivery`
- Packet refresh role: `feature-fixer required-fixes packet-tightening v2`

## Packet Traceability Note

- Review scope remains the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- This follow-up refresh is metadata only and exists to satisfy the reviewer's required packet fixes without broadening implementation scope.
- This packet refresh states the non-expansion boundary explicitly: it adds no new workflow actions, no new command coverage, and no new engine behavior.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the deterministic CLI contract for the already-exposed `bootstrap` entrypoint so the current `open project/document` demo-path step keeps a canonical, drift-resistant compatibility surface while Textual remains disabled. This slice adds no new workflow actions, no new command coverage, and no new engine behavior.

## Canonical Demo-Path Step Advanced

- Exact step advanced: `open project/document`.
- Why this step: `bootstrap` is the current CLI entrypoint for that step, and this slice makes it more real by preventing silent parser/catalog drift from changing the operator-facing command contract.
- Scope boundary: this is contract-hardening only. It does not add new workflow actions, new command coverage, retrieval behavior, patch behavior, save behavior, or any new engine business logic.

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

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares the CLI parser surface against `command_names()` and raises `ValueError` when the exposed command surface drifts from the declared catalog. This removes a silent-contract-drift blocker from the `open project/document` demo-path step.
- Kept the returned CLI contract aligned with canonical command order by returning the validated canonical tuple instead of rebuilding a separate order from parser tokens. This removes parser-order ambiguity from the `open project/document` demo-path step.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection. This removes a smoke-test coverage gap around the `open project/document` demo-path step.
- Reissued the handoff packet as a narrow command-catalog slice so the claimed roadmap and vision impact matches the actual implementation.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and lane size limits.
- Implementation scope stayed limited to one owned command file plus one approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. `open project/document`: hardened `command_cli_contract()` to fail fast when the parser surface drifts from the canonical command catalog, removing the blocker where the `bootstrap` operator contract could change silently.
2. `open project/document`: preserved canonical command ordering in the returned CLI contract, removing the blocker where parser token order could diverge from the declared catalog order.
3. `open project/document`: added regression coverage for canonical-order alignment and drift rejection, removing the blocker where this compatibility contract could regress without a focused smoke-test failure.
4. `open project/document`: tightened the handoff packet so it names the exact demo-path step advanced and the concrete blocker removed, satisfying the AGENTS handoff requirement for active-lane plan alignment.

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

- Risk: `MEDIUM`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the existing `bootstrap` command contract deterministic and drift-resistant for the `open project/document` step.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the already-exposed `bootstrap` entrypoint.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable because parser drift now fails fast instead of silently changing the `bootstrap` operator contract used for `open project/document`.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

## Scope-check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: runtime edits stay in lane-owned `src/qual/commands/**`, and the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
