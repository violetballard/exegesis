# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical operator CLI step `open project/document` more real in the current CLI-first MVP loop by keeping its command contract deterministic and rejecting parser-surface drift against the catalog.
- Risk reason: the branch includes the approved shared-test path `tests/unit/test_commands_catalog.py`, so this fixer pass stays on the high-risk template even though the current refresh is metadata only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Verify the current branch tip contains the reviewer-requested parser-surface hardening for the canonical `open project/document` CLI step in the command catalog.
2. Verify focused regression coverage exists for alias substitution, extra entrypoint, dropped entrypoint, and reordered entrypoint drift.
3. Re-run the required local gates and record outcomes for this fixer pass.
4. Refresh handoff metadata without counting that refresh as implementation scope.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: this fixer pass verified that the branch already contains the parser-surface contract fix that hardens the canonical `open project/document` CLI step and will refresh the packet to the real review basis.
- First green tests: satisfied by the full gate rerun recorded below on `2026-04-18`.
- Before risky/shared file edit: the only shared-file implementation path remains the approved test exception `tests/unit/test_commands_catalog.py`.
- Ready for handoff: satisfied by this packet refresh and the green gate suite recorded below.

## Packet Traceability Note

- Current implementation review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Review basis choice: re-review should stay anchored to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, which is the command-catalog implementation commit the reviewer inspected for the required fixes below.
- Metadata-only rule: later packet refresh commits on this branch are metadata only unless a regenerated handoff explicitly says otherwise, so they do not expand the implementation review scope for this resubmission.
- Reviewer-fix implementation files in scope at that review basis:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only files for this fixer refresh:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. This handoff packet now names the canonical demo-path step advanced by the reviewed change: the operator CLI step `open project/document`.
2. The roadmap and vision mapping are now tightened to the exact operator-facing contract strengthened by the reviewed diff: deterministic CLI command ordering and fail-fast parser/catalog drift detection for the CLI-first MVP loop.
3. Re-review remains anchored to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and later packet refresh commits are preserved as metadata only for this resubmission.

## Resubmission Refresh

- Refresh date: `2026-04-18`
- Refresh purpose: leave a new metadata-only fixer commit that records the fresh full gate rerun against the current branch tip while keeping re-review anchored to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Plan-alignment note: this resubmission is specifically for the canonical operator CLI step `open project/document`; it makes that step more real in the current CLI-first MVP loop by ensuring the parser-facing CLI surface stays identical to the declared command catalog and fails fast if it drifts.
- Review request: treat this packet as the current source of truth for the `feat-commands` re-review.

## Canonical Demo-Path Step Advanced

- Canonical demo-path step advanced: operator CLI step `open project/document`.
- Demo-path loop: this is the front-door step of the current MVP operator path that must reliably support the CLI-first flow `vault -> context -> run -> patch -> export` before `Exegesis Console` exists.
- Narrow mapping: this `feat-commands` change is contract-hardening for the existing CLI path only, not new command capability or CLI UX expansion.
- Specific path impact: it makes only the existing `open project/document` CLI step more reliable by forcing the accepted parser surface to stay identical to the declared command catalog before the operator can continue into retrieval, review, and export.
- Concrete effect: the accepted CLI parser surface now fails fast if canonical tokens, alias entrypoints, or their order drift away from the declared command catalog.
- Concrete blocker removed: without this guard, the CLI can silently accept a parser surface that no longer matches the documented command catalog for `open project/document`, which undermines the Milestone 3 operator loop at its entry step.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the reviewed command catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` keeps the canonical CLI contract aligned to catalog order and rejects parser/catalog drift.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` at that same reviewed implementation commit for canonical-order alignment and parser/catalog drift rejection.
- Scope guard: this resubmission does not add new commands, new flags, or CLI UX expansion; it only hardens the existing `open project/document` CLI contract on the current MVP path so the operator can enter the CLI-first workflow without parser/catalog drift.

## Metadata-Only Fixer Refresh

- Refreshed the handoff packet so re-review uses the real current implementation basis instead of the stale `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` anchor.
- Re-ran the required local gates for this fixer pass and recorded the current outcomes below.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff stayed within the `4`-task cap, `30m` time budget, and the lane size limits.
- This fixer refresh only edits `THREAD.md` and `THREAD_PACKET.md`; the implementation under review remains inside the owned command paths plus the approved shared test file.

## Approved Exception Note

- Shared-test exception for `tests/unit/test_commands_catalog.py` is explicitly approved in lane policy enforcement for `codex/feat-commands` in `scripts/scope-check.sh`.
- Approver: `Violet Ballard`.
- Approval reference: commit `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` (`fix(commands): align feat-commands handoff policy`), which added the `tests/unit/test_commands_catalog.py` shared-test allowance for this lane.
- Approval confirmation: commit `c3a66bb580772d65201a630d673a8de1d4a63776` (`fix(commands): tighten feat-commands packet and policy`).
- Approval date: `2026-03-28` (`Sat Mar 28 17:34:01 2026 -0700`; confirmation at `Sat Mar 28 20:24:01 2026 -0700`).

## Handoff Packet

- Branch name: `codex/feat-commands`

### Implementation Tasks Completed (Numbered)

1. Verified that implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` contains the reviewed `command_cli_contract()` hardening in `src/qual/commands/catalog.py`.
2. Verified that implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` contains the focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.

### Metadata-Only Fixer Actions

- Refreshed the handoff packet so it keeps re-review anchored to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Re-ran the required local gates and recorded outcomes for this fixer pass.
- Tightened the roadmap/vision justification so the packet maps the work to the active CLI-first MVP loop instead of broad CLI stability language.

### Files Changed

- Implementation files in the current review basis:
  - `src/qual/commands/catalog.py`
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
- Verification timestamp (UTC): `2026-04-18T22:14:54Z`

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: future command-surface changes still require the catalog, exports, and focused parser-surface tests to remain aligned by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3 / current MVP loop justification: the active engine-side CLI-first path must reliably execute `vault -> context -> run -> patch -> export`, and this change hardens the `open project/document` entry step that launches that loop.
- `feat-commands`: lock the parser-facing command contract for the existing `open project/document` operator path so later retrieval, review, and export steps start from a deterministic CLI surface.
- Concrete blocker removed: contract-build now rejects parser/catalog drift before the CLI-first Milestone 3 loop can start from a silently divergent `open project/document` entrypoint.

### Vision capability affected

- Operator-first control surface: CLI remains the first-class MVP surface, and the `open project/document` entrypoint now stays deterministic across catalog, exports, and parser wiring.
- No silent output or contract drift: parser/catalog drift now fails loudly before silently changing the operator contract that starts the CLI-first loop.

### Routing/provider impact note

- None. This change only affects local command-contract validation, lane-owned command exports, and focused command-catalog test coverage.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation paths stay inside `src/qual/commands/**`
  - approved shared test path is `tests/unit/test_commands_catalog.py`
  - approval trace: `scripts/scope-check.sh`, commit `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` on `2026-03-28`, authored by `Violet Ballard`, with confirmation in `c3a66bb580772d65201a630d673a8de1d4a63776`
- Shared-file approval traceability:
  - approver: `Violet Ballard`
  - approval reference: `scripts/scope-check.sh` allowance added by commit `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` (`fix(commands): align feat-commands handoff policy`)
  - approval date: `2026-03-28`
  - enforcement evidence: `SCOPE_ALLOW_SHARED=1 make scope-check` passed on this branch, which is the lane-local gate path for approved shared-file edits
