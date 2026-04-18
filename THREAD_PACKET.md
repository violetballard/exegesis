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

1. Regenerate the handoff packet so it reflects the live `feat-commands` branch state rather than the older review anchor.
2. Keep the explicit canonical demo-path step mapping required by `AGENTS.md`.
3. Confirm the reviewer-requested parser-surface fixes remain represented in the packet and backed by the checked-in tests.
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

- Plan complete: this fixer pass regenerates the packet against the live branch state and does not expand the implementation scope.
- First green tests: satisfied by the full gate rerun recorded below.
- Before risky/shared file edit: the only shared-file scope remains the approved test exception `tests/unit/test_commands_catalog.py`.
- Ready for handoff: satisfied by this refreshed packet and the full gate rerun recorded below.

## Packet Traceability Note

- Current branch tip for re-review: `f42c2a9b9ae183fadc893982c2cf90aec8c0c705`.
- The earlier review anchor `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` is superseded by later lane-owned command-surface work on this branch.
- Reviewer-fix implementation remains in scope at:
  - `543632d5` - `fix(commands): reject cli token drift`
  - `0f4de989` - `fix(commands): satisfy reviewer required fixes`
- Reviewed implementation files in scope:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files for this fixer refresh:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. Tightened the CLI contract so parser-surface drift is rejected against the declared catalog-backed parser surface, not just against deduplicated canonical names.
2. Added regression coverage for alias substitution, token reordering, extra entrypoints, removed entrypoints, and normalized alias drift in `tests/unit/test_commands_catalog.py`.
3. Kept the explicit canonical demo-path mapping required by `AGENTS.md`: this work advances `open project/document`.
4. Regenerated this packet so re-review evaluates the live branch state instead of the stale `f8d860ed...` anchor, then re-ran the required gate suite.

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
- Why this step: `feat-commands` owns the CLI operator surface that starts the current MVP loop, and the branch’s command-surface contract work keeps that entry step deterministic and smoke-testable while Textual remains disabled.
- Concrete effect: `command_cli_contract()` now preserves canonical command order and rejects parser-surface drift such as alias-for-canonical substitution, token reordering, added entrypoints, or removed expected entrypoints, so the operator-facing command contract for starting the workflow cannot silently change.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full accepted parser surface against the command catalog and raises `ValueError` if canonical entrypoints, alias entrypoints, or entrypoint order drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser-surface drift rejection, including alias substitution, entrypoint reordering, added entrypoints, and removed expected entrypoints.
- Refreshed the handoff packet so re-review evaluates the live branch state with explicit demo-path alignment.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff stayed within the `4`-task cap, `30m` time budget, and the lane size limits.
- The implementation slice remains limited to one owned command file plus one approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Confirmed the live branch already contains the reviewer-requested parser-surface hardening in `src/qual/commands/catalog.py`.
2. Confirmed the live branch already contains the requested regression coverage in `tests/unit/test_commands_catalog.py`, including alias-substitution drift cases.
3. Regenerated the handoff packet so it maps this work explicitly to `open project/document` and reflects the current branch tip instead of the stale review anchor.
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
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the `open project/document` operator entry contract and its parser-surface determinism.

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
