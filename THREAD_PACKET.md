# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the `feat-commands` CLI contract deterministic, reject parser-surface drift against the catalog, and resubmit an accurate handoff packet against the branch state that now contains those fixes.
- Risk reason: the branch includes the approved shared-test path `tests/unit/test_commands_catalog.py`, so this fixer pass stays on the high-risk template even though the current refresh is metadata only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Verify the current branch tip contains the reviewer-requested parser-surface hardening in the command catalog.
2. Verify focused regression coverage exists for alias substitution, extra entrypoint, dropped entrypoint, and reordered entrypoint drift.
3. Regenerate the handoff packet so it matches the actual implementation state being resubmitted instead of the stale historical anchor.
4. Re-run the required local gates and record outcomes for this fixer pass.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: this fixer pass verified that the branch already contains the parser-surface contract fix and will refresh the packet to the real review basis.
- First green tests: satisfied by the full gate rerun recorded below on `2026-04-18`.
- Before risky/shared file edit: the only shared-file implementation path remains the approved test exception `tests/unit/test_commands_catalog.py`.
- Ready for handoff: satisfied by this packet refresh and the green gate suite recorded below.

## Packet Traceability Note

- Current implementation review basis: `5b2ecba061b28cca27eddd587414d52c702aa628`.
- Review basis choice: this fixer commit is metadata only. Re-review should inspect the implementation already present at `5b2ecba061b28cca27eddd587414d52c702aa628`, which includes the parser-surface contract hardening, the required regression coverage, and the later lane-owned command-surface follow-on work already on this branch.
- Reviewer-fix implementation files in scope at that review basis:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Additional lane-owned branch-tip implementation file present at that review basis:
  - `src/qual/commands/__init__.py`
- Metadata-only files for this fixer refresh:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. `command_cli_contract()` now validates the full accepted CLI parser surface against the catalog-derived declared entrypoints and raises `ValueError("Command CLI parser surface is inconsistent")` when aliases, ordering, or accepted entrypoints drift.
2. Focused regression coverage now proves rejection of alias substitution, extra entrypoint, dropped entrypoint, and reordered entrypoint drift in `tests/unit/test_commands_catalog.py`.
3. This handoff packet now matches the actual implementation state being resubmitted and records a fresh full gate rerun for `2026-04-18`.

## Resubmission Refresh

- Refresh date: `2026-04-18`
- Refresh purpose: leave a new metadata-only fixer commit that records a fresh full gate rerun against the current branch tip and keeps the packet anchored to the actual implementation state already on this branch.
- Review request: treat this packet as the current source of truth for the `feat-commands` re-review.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Canonical Demo-Path Step Advanced

- Primary Milestone 3 engine-first demo-path step advanced: `open project/document`.
- Operator-step mapping: this change makes the CLI `open project/document` step more reliable by forcing the accepted parser surface to stay identical to the declared command catalog.
- Concrete effect: the accepted CLI parser surface now fails fast if canonical tokens, alias entrypoints, or their order drift away from the declared command catalog.
- Concrete blocker removed: without this guard, the CLI can silently accept a parser surface that no longer matches the documented command catalog, which makes the `open project/document` operator step unreliable for smoke tests.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default command catalog validates the full accepted parser surface instead of only the deduplicated canonical-name projection.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for alias substitution, reordered parser entrypoints, extra entrypoints, dropped entrypoints, and related parser-surface drift cases.
- Preserved deterministic catalog helpers and branch-tip lane-owned command-surface exports in `src/qual/commands/__init__.py`.
- Refreshed the handoff packet so re-review uses the real current implementation basis instead of the stale `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` anchor.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff stayed within the `4`-task cap, `30m` time budget, and the lane size limits.
- This fixer refresh only edits `THREAD.md` and `THREAD_PACKET.md`; the implementation under review remains inside the owned command paths plus the approved shared test file.

## Approved Exception Note

- Shared-test exception for `tests/unit/test_commands_catalog.py` is traceable to the lane policy approval recorded in `scripts/scope-check.sh`.
- Approver / policy author: `Violet Ballard`.
- Approval reference: commit `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` (`fix(commands): align feat-commands handoff policy`), plus the follow-up tightening commit `c3a66bb580772d65201a630d673a8de1d4a63776` (`fix(commands): tighten feat-commands packet and policy`).
- Approval date: `2026-03-28`.
- Approver: the approval already carried in the reviewed `feat-commands` feature packet that this fixer run was instructed to treat as the source of truth for shared-file exceptions.
- Approval reference/date: reviewer packet section `Approved exception note` in the fixer input for this run, refreshed on `2026-04-18`, plus branch-local enforcement evidence from `SCOPE_ALLOW_SHARED=1 make scope-check`.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Verified that the current branch tip already contains the reviewer-requested parser-surface validation in `src/qual/commands/catalog.py`.
2. Verified that the required regression tests for alias substitution, extra entrypoints, dropped entrypoints, and reordered entrypoints are present and passing in `tests/unit/test_commands_catalog.py`.
3. Refreshed the handoff packet so it points to the actual current implementation review basis `5b2ecba061b28cca27eddd587414d52c702aa628` instead of the stale historical anchor.
4. Re-ran the required local gates and recorded outcomes for this fixer pass.

### Files Changed

- Implementation files in the current review basis:
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only files changed in this fixer pass:
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
- Verification timestamp (UTC): `2026-04-18T21:00:01Z`

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: future command-surface changes still require the catalog, exports, and focused parser-surface tests to remain aligned by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility at the `open project/document` entry step of the engine-first MVP path.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- Concrete Milestone 3 blocker removed: the branch now rejects parser/catalog drift at contract-build time, so the CLI entry surface cannot silently diverge from the command catalog that operators and downstream engine-loop smoke tests rely on.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable and deterministic for the command entry surface.
- Auditable state and workflow - the command surface now fails loudly on parser/catalog drift instead of silently changing the operator contract.

### Routing/provider impact note

- None. This change only affects local command-contract validation, lane-owned command exports, and focused command-catalog test coverage.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation paths stay inside `src/qual/commands/**`
  - approved shared test path is `tests/unit/test_commands_catalog.py`
  - approval trace: `scripts/scope-check.sh`, commits `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` and `c3a66bb580772d65201a630d673a8de1d4a63776` on `2026-03-28`, authored by `Violet Ballard`
- Shared-file approval traceability:
  - approver: prior `feat-commands` packet approval carried forward into the reviewer packet supplied to this fixer run
  - approval reference: fixer input source-of-truth line `Approved exception note - Approved shared-test exception for tests/unit/test_commands_catalog.py`
  - approval date: `2026-04-18` reviewer packet refresh used for this fixer pass
  - enforcement evidence: `SCOPE_ALLOW_SHARED=1 make scope-check` passed on this branch, which is the lane-local gate path for approved shared-file edits
