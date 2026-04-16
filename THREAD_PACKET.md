# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix metadata refresh`

## Packet Traceability Note

- Keep the approval basis pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- This packet refresh is metadata-only and exists to satisfy the reviewer's required fixes without changing the reviewed implementation scope.
- Re-review basis: the packet now states the exact canonical demo-path step advanced and the concrete CLI contract blocker removed, matching the reviewer's numbered required fixes.
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

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, reuses the canonical command order, and rejects canonical CLI name/order drift between the parser lookup table and the command catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `open project/document`.
- Supporting CLI-fallback steps kept smoke-testable by the same contract hardening: `retrieve relevant material` and `preview and apply or reject a patch`.
- AGENTS alignment statement: this packet explicitly maps the work to the `open project/document` step of the canonical demo path so the handoff names the concrete step this slice makes more real.
- Why this step is strengthened: the operator reaches that step through the CLI-first command surface today, so keeping `command_cli_contract()` deterministic, preserving canonical command ordering, and rejecting canonical-name/order drift between the CLI lookup table and the command catalog prevents the entry command surface from silently changing underneath the engine-first MVP loop.
- Concrete blocker removed: Milestone 3 requires that the CLI can still execute the MVP loop while Textual remains disabled. Before this slice, `command_cli_contract()` rebuilt canonical names from the parser lookup table without verifying they still matched `command_names()`, which could silently destabilize the `open project/document` operator path. This change turns that canonical-name/order mismatch into an immediate contract error instead of a silent operator-surface regression.
- Secondary effect only: the same deterministic contract keeps the existing CLI fallback smoke-testable for downstream demo-path steps, including `preview and apply or reject a patch`, but this handoff is anchored to `open project/document` as the primary justified step.

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

## High-Risk Rationale

- This handoff uses the high-risk template because it tightens a public CLI command contract and includes the approved shared-test file `tests/unit/test_commands_catalog.py`.
- Scope remains narrow: command-surface contract hardening only.
- Non-goals confirmed: no new command behavior, no engine logic changes, and no routing/provider changes.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the canonical CLI name/order surface drifts from the command catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Regenerated the handoff packet as a metadata-only refresh so the review scope stays pinned to the command-catalog implementation commit and includes the explicit demo-path mapping requested in review.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap, 30-minute budget, and the lane size limits.
- The implementation slice stayed limited to one owned command file plus one focused non-owned test file, so the handoff remains narrow and reviewable.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It is the only non-owned implementation path in this handoff.

## Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name/order consistency against `command_names()` and fail fast on canonical CLI contract drift.
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

- `Milestone 3: Real workflow loop` - this change strengthens the requirement that the CLI can still execute the MVP loop while Textual remains disabled by hardening the `open project/document` entry step against silent CLI lookup-table/catalog canonical-order drift.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- Plan-alignment note: this is a contract-hardening slice, not a UX expansion; it directly removes a concrete blocker on the canonical demo path because the CLI entry-command surface now fails fast if the CLI lookup table's canonical-name order stops matching the catalog order expected by the engine-first operator flow.

### Vision capability affected

- `Canonical engine contract` - the CLI-side `open project/document` entry contract now stays aligned with the canonical command catalog instead of silently diverging when the CLI lookup table's canonical-name order drifts.
- `Auditable state and workflow` - CLI lookup-table/catalog canonical-order drift now fails loudly at contract construction time, making operator-facing command behavior explicit and traceable for the active MVP loop.
- Demo-path alignment note: this hardening primarily protects the `open project/document` entry step and secondarily preserves a stable, smoke-testable CLI fallback surface for `retrieve relevant material` and `preview and apply or reject a patch` while Textual remains disabled.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.
