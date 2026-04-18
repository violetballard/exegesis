# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: reissue the reviewer packet without changing the approved command implementation, while making the metadata-only refresh fully auditable and explicitly tying the reviewed command-catalog check to the canonical `open project/document` demo-path step.
- Risk reason: this fixer pass touches shared handoff metadata (`THREAD.md`, `THREAD_PACKET.md`) and must preserve the existing implementation approval basis exactly.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Restore the packet’s implementation review anchor to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Fully enumerate the metadata files touched by the packet-refresh commit, including `THREAD.md`.
3. Amend the roadmap/vision mapping so it names `open project/document`, the concrete parser/catalog drift failure it prevents, and why that matters to the active CLI-first MVP loop.
4. Re-run the required gates on the current worktree, record the outcomes, and leave a packet-only fixer commit for re-review.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: the reviewer’s required fixes are limited to packet traceability and file inventory completeness.
- First green tests: full required gate suite rerun on `2026-04-18`.
- Before risky/shared file edit: only `THREAD.md` and `THREAD_PACKET.md` are edited in this fixer pass.
- Ready for handoff: the packet again names `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as the implementation review target and fully enumerates the metadata-only refresh files.

## Packet Traceability Note

- Implementation review target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Implementation review basis: the approved command implementation remains the change reviewed in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Metadata-only refresh commit called out by the reviewer: `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`
- Metadata-only files touched by that refresh commit:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Metadata-only files touched by this fixer pass:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Approval basis preserved: later commits are treated as metadata-only only where this packet explicitly enumerates those metadata files.

## Reviewer Required Fixes Satisfied

1. The packet now names the exact canonical demo-path step advanced by the reviewed implementation: `open project/document`.
2. The scope justification now states the concrete operator-path failure being prevented: silent parser/catalog drift changing the bootstrap CLI entrypoint contract.
3. The roadmap/vision mapping now explains why that check is necessary for the active CLI-first MVP loop while Textual remains disabled, not as general infrastructure hardening.
4. The `Files changed` inventory still includes every file touched by the reviewer-cited packet-refresh commit `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`, including `THREAD.md`.
5. The implementation review target remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and this fixer pass remains packet-only.

## Scope Completed

- Preserved the original implementation approval basis at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Corrected the packet so the metadata-refresh inventory is complete and auditable.
- Stated the exact canonical demo-path step this lane hardens and the concrete CLI operator-path failure the reviewed command-catalog check prevents.
- Re-ran the required gates after the metadata correction.
- Scope boundary: no changes to `src/qual/commands/**` or test implementation in this fixer pass.

## Kickoff Budget / Limits Compliance

- High-risk fixer pass stayed within the `4`-task cap, `30m` budget, and lane size limits.
- This fixer pass changed only `THREAD.md` and `THREAD_PACKET.md`.

## Approved Exception Note

- Approved shared-test paths for the reviewed implementation:
  - `tests/unit/test_commands_catalog.py`
- This fixer pass does not edit shared tests.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Restored the packet traceability note so `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` remains the implementation review target.
2. Completed the metadata-only `Files changed` inventory for the reviewer-cited packet-refresh commit `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`, including `THREAD.md`.
3. Rewrote the roadmap/vision mapping so it names `open project/document`, the parser/catalog drift blocker, and the CLI-first MVP-loop rationale directly in the handoff fields.
4. Re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Files Changed

- Reviewed implementation target `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only files changed by packet refresh commit `6ee4015b1b62fb44c2b81ac19be7cbf03440313f`:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Metadata-only files changed by this fixer pass:
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
- Remaining risk: process auditability now depends on reviewers using the preserved implementation target `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and the enumerated metadata-only files above.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: preserve CLI compatibility while the package/layout migration lands so the canonical demo path can reliably start at `open project/document` while Textual remains disabled.
- `feat-commands`: keep the CLI entrypoint catalog for `open project/document` migration-safe and deterministic so the CLI-first MVP loop does not silently drift away from the reviewed command contract.

### Vision capability affected

- Writing-centered workflow: the canonical `open project/document` step remains reachable through a stable CLI entrypoint instead of a silently drifted parser surface.
- Canonical engine contract: the reviewed command-catalog check fails fast if the parser surface stops matching the catalog order used by the engine-facing CLI contract.

### Canonical demo-path step advanced

- Step advanced: `open project/document`
- Concrete blocker removed: without the reviewed `command_cli_contract()` consistency check, the CLI parser surface could drift from the canonical command catalog and still build a contract, which would let the operator-facing bootstrap entrypoint silently move out of sync with the reviewed MVP command order.
- Why this is MVP-loop-specific: this lane keeps the active CLI-first engine loop trustworthy while Textual is disabled by making the very first operator step fail loudly on parser/catalog drift instead of degrading into an ambiguous or stale startup contract.

### Routing/provider impact note

- None.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - reviewed implementation stays in lane-owned `src/qual/commands/**`
  - this fixer pass edits only `THREAD.md` and `THREAD_PACKET.md`
