# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the CLI command contract so `command_cli_contract()` stays deterministic, preserves canonical command order, and fails fast if accepted parser entrypoints drift from the catalog.
- Risk reason: this slice uses the approved shared-test exception for `tests/unit/test_commands_catalog.py`, so it stays on the high-risk template even though implementation remains command-catalog-only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Add the missing handoff field that explicitly names the canonical demo-path step advanced by this work.
2. Tighten the scope statement so the roadmap and vision mapping stay tied to that concrete demo-path step.
3. Keep the reviewed implementation scope aligned to the command-catalog slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
4. Re-run the required local gates and record outcomes for re-review.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: this fixer pass is limited to the reviewer-required packet fixes; no new implementation defect was identified.
- First green tests: satisfied by the full gate rerun recorded below.
- Before risky/shared file edit: the only shared-file scope remains the approved test exception `tests/unit/test_commands_catalog.py`.
- Ready for handoff: satisfied by this refreshed packet and the full gate rerun recorded below.

## Packet Traceability Note

- Review the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Treat later packet-refresh commits as metadata-only unless this handoff is regenerated again.
- Reviewed implementation files in scope:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files for this fixer refresh:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. Added the explicit canonical demo-path handoff field required by the reviewer.
2. Tightened the scope statement so it stays framed as CLI-first command-contract hardening for that concrete demo-path step.
3. Kept the reviewed implementation scope aligned to the command-catalog slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
4. Re-ran the required gate suite and recorded fresh outcomes for this metadata-only fixer pass.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Canonical Demo-Path Step Advanced

- Primary step advanced: `open project/document`.
- Why this step: `feat-commands` owns the CLI operator surface that starts the current MVP loop, and this command-catalog hardening keeps that entry step deterministic and smoke-testable while Textual remains disabled.
- Concrete effect: `command_cli_contract()` now preserves canonical command order and rejects parser-surface drift such as alias-for-canonical substitution, token reordering, added entrypoints, or removed expected entrypoints, so the operator-facing command contract for starting the workflow cannot silently change.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full accepted parser surface against the command catalog and raises `ValueError` if canonical entrypoints, alias entrypoints, or entrypoint order drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser-surface drift rejection, including alias substitution and entrypoint reordering.
- Refreshed the handoff packet so re-review evaluates the command-catalog slice with explicit demo-path alignment.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff stayed within the `4`-task cap, `30m` time budget, and the lane size limits.
- The implementation slice remains limited to one owned command file plus one approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Added the explicit canonical demo-path mapping for this handoff: `open project/document`.
2. Tightened the scope statement so the roadmap and vision mapping stay specific to CLI-first command-contract hardening at that step.
3. Kept the reviewed implementation scope aligned to `src/qual/commands/catalog.py` plus the approved shared test `tests/unit/test_commands_catalog.py`.
4. Re-ran the required local gates and recorded outcomes for this fixer pass.

### Files Changed

- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification date: `2026-04-18`

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: future parser-surface changes still require the catalog and command tests to be updated together by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands, specifically at the `open project/document` entry step of the engine-first MVP path.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the `open project/document` operator entry contract.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable and deterministic while Textual stays disabled.
- Auditable state and workflow - the command surface now fails loudly on parser/catalog drift instead of silently changing the operator contract.

### Routing/provider impact note

- None. This change only affects local command-contract validation and focused command-catalog test coverage.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation path stays inside `src/qual/commands/**`
  - approved shared test path is `tests/unit/test_commands_catalog.py`
