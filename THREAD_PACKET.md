# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: satisfy the reviewer-required fixes by making `command_cli_contract()` reject real parser-surface drift, adding focused regressions for those drift cases, and updating the handoff packet to name the exact canonical demo-path step this protects.
- Risk reason: this fixer pass touches the shared command contract and shared handoff metadata while preserving the CLI-first Milestone 3 surface.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Extend the command catalog so CLI entrypoints are declared per command spec and the contract can validate the full parser surface, not only canonical-name order.
2. Add regressions for parser-surface drift that preserves canonical command names but changes accepted CLI entrypoints.
3. Update the handoff packet so it explicitly maps this work to the canonical `open project/document` demo-path step and the concrete blocker removed.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: the remaining work is the command-contract hardening the reviewer asked for plus packet alignment.
- First green tests: recorded after the full required gate suite on `2026-04-18`.
- Before risky/shared file edit: `THREAD.md` and `THREAD_PACKET.md` are shared metadata paths; the command catalog is a public CLI contract.
- Ready for handoff: branch includes command-catalog enforcement, focused parser-drift regressions, and corrected handoff metadata.

## Packet Traceability Note

- Reviewer snapshot called out implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and requested additional fixes before re-review.
- Current branch state carries those fixes forward on top of that snapshot instead of preserving it as the final implementation anchor.
- Current implementation under review lives in:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Current handoff metadata for this fixer pass lives in:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. `command_cli_contract()` now validates the declared parser surface, not just the deduplicated canonical-name projection, so alias substitution, canonical-token removal, and entrypoint reordering fail fast.
2. Focused regressions cover parser-surface drift that still preserves canonical command names, including the reviewer-described case where an alias remains accepted while the canonical token is dropped.
3. The handoff packet now names the exact canonical demo-path step advanced: `open project/document`.
4. The handoff packet now states the concrete blocker removed: silent parser/catalog drift changing the operator-facing bootstrap CLI contract while the CLI remains the active MVP surface.

## Scope Completed

- Extended `CommandSpec` with explicit CLI-surface metadata so parser entrypoints are declared by the catalog rather than inferred indirectly.
- Hardened `command_cli_contract()` and related helpers to reject parser-surface drift even when canonical command order still appears correct.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for missing canonical entrypoints, alias substitution, and reordered accepted entrypoints.
- Corrected the handoff metadata so it reflects the actual branch state and the canonical demo-path step strengthened by this work.

## Kickoff Budget / Limits Compliance

- High-risk fixer pass stayed within the `4`-task cap and focused on one lane-owned implementation file, one approved shared test file, and two handoff metadata files.
- Net scope stayed within the lane handoff boundaries described above.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Declared per-command CLI entrypoints in the command catalog so the parser surface is explicit and reviewable.
2. Tightened `command_cli_contract()` validation so parser/catalog drift fails even when canonical names still line up.
3. Added regression tests for the parser-drift cases required by review.
4. Updated the packet and thread pointer so the handoff explicitly maps to `open project/document` and the active CLI-first MVP loop.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

### Risks / Blockers

- Risk: `MEDIUM`
- Remaining risk: the command catalog now carries more explicit CLI-surface metadata, so future command additions need to keep aliases, CLI tokens, and smoke/demo contracts aligned.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: preserve CLI compatibility while the package/layout migration lands so the canonical demo path can reliably start at `open project/document` while Textual remains disabled.
- `feat-commands`: keep the CLI entrypoint catalog deterministic and migration-safe for the engine-first MVP loop.

### Vision capability affected

- Writing-centered workflow: the canonical `open project/document` step remains reachable through a stable bootstrap CLI surface.
- Canonical engine contract: the CLI contract now fails fast when the parser surface drifts away from the reviewed command catalog instead of silently accepting a stale or ambiguous entrypoint surface.

### Canonical demo-path step advanced

- Step advanced: `open project/document`
- Concrete blocker removed: the CLI parser could previously drift away from the canonical bootstrap entrypoint surface while still producing the same canonical-name projection, which risked silently changing the operator’s first step in the MVP loop.
- Why this is MVP-loop-specific: while Textual is disabled, the CLI bootstrap command is the active operator entry into the engine workflow, so this check keeps the first demo-path step deterministic and auditable.

### Routing/provider impact note

- None.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - lane-owned implementation: `src/qual/commands/catalog.py`
  - approved shared test: `tests/unit/test_commands_catalog.py`
  - shared metadata updated for handoff accuracy: `THREAD.md`, `THREAD_PACKET.md`
