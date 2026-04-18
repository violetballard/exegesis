# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: reissue the `feat-commands` handoff packet so it preserves the original command-catalog review target, fully enumerates the metadata refresh files, and stays auditable for re-review.
- Risk reason: this is a shared-file packet correction and the implementation slice still includes the approved shared test file `tests/unit/test_commands_catalog.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet to implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Preserve the metadata-only treatment for the later packet-refresh commit while fully enumerating the metadata files it touched.
3. Re-run the required gates on the current tree and record the outcomes.
4. Leave a packet-only fixer commit for re-review.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: reviewer fixes reduced to packet traceability only, so the implementation review basis remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- First green tests: required gate reruns are recorded below for the current tree on `2026-04-18`.
- Before risky/shared file edit: only `THREAD.md` and `THREAD_PACKET.md` are being edited in this fixer pass.
- Ready for handoff: the packet now preserves the original approval basis and fully lists the metadata refresh files.

## Packet Traceability Note

- Reviewed implementation target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh commit: `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Traceability rule for this resubmission: review the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and treat later packet-refresh commits as metadata-only because this refreshed packet fully enumerates the metadata files they changed.

## Reviewer Required Fixes Satisfied

1. The `Files changed` section now includes every file touched by packet-refresh commit `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`, including `THREAD.md`.
2. The approval basis is preserved explicitly: the implementation review target remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and later commits are treated as metadata-only only because the refreshed packet fully enumerates those metadata files.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- This fixer pass does not change command implementation. It only corrects packet traceability so the original command-catalog review slice remains auditable.

## Kickoff Budget / Limits Compliance

- High-risk fixer pass stayed within the `4`-task cap, `30m` budget, and lane size limits.
- This fixer pass changed only `THREAD.md` and `THREAD_PACKET.md`.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`. It remains the only non-owned implementation path in the reviewed command-catalog slice.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Restored the packet’s implementation review target to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Updated the metadata inventory so packet-refresh commit `6ee4015b1b62fb44c2b81ac19be7cbf03440313f` is explicitly recorded as touching both `THREAD.md` and `THREAD_PACKET.md`.
3. Re-ran the required gate suite on the current tree and recorded the outcomes below.
4. Reissued the handoff packet so the metadata-only refresh remains auditable without expanding the implementation review scope.

### Files Changed

- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files touched by packet-refresh commit `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`:
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
- Remaining risk: none beyond normal metadata drift risk if future packet refreshes are not fully enumerated.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop. Preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands`: CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected

- Canonical engine contract: CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow: the command surface fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing/provider impact note

- None. This change only affects local command contract validation and focused command-catalog test coverage.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation path stays inside `src/qual/commands/catalog.py`
  - approved shared test path is `tests/unit/test_commands_catalog.py`
  - this fixer pass edits only `THREAD.md` and `THREAD_PACKET.md`
