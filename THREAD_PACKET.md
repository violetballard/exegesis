# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the CLI-first MVP demo loop self-describing by preserving logical flow-step metadata for shim-backed terminal commands used for patch apply/reject, persist, and export handoff.
- Risk reason: reviewed implementation includes one approved shared regression file, `tests/unit/test_commands_catalog.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Inspect the feat-commands catalog contracts and identify a deterministic demo-path gap inside lane-owned code.
2. Fix the flow-step labeling for shim-backed demo-loop commands without broadening command behavior or touching shared CLI entrypoints.
3. Update focused regression coverage for the corrected trusted-surface, workflow, compatibility, and next-action metadata.
4. Refresh the handoff packet after focused unit coverage and the required gate suite.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- integrator-locked/shared-by-approval edits needed
- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit pinned for re-review: `06540160de4cf0d452c1ed9b4d4926c205888be9`
- Later commits on this branch are metadata-only packet refreshes unless a regenerated handoff explicitly broadens implementation review scope
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Scope Completed

- Hardened `command_cli_contract()` so it rejects parser-surface drift, including alias-only substitutions, token removals, token additions, and entrypoint reordering that would otherwise leave canonical command names unchanged.
- Fixed `_resolve_demo_loop_token()` so demo-loop resolution preserves the logical demo token as the flow step when a shim-backed terminal command is selected for `apply-patch`, `reject-patch`, or `persist`.
- Corrected the downstream demo workflow metadata generated from that loop resolution so the canonical CLI MVP path now reports:
  - `apply-patch` as `apply-patch`
  - `reject-patch` as `reject-patch`
  - `persist` as `persist`
  - `export-handoff` as `export-handoff`
- Updated focused regression tests to lock the corrected flow-step metadata across:
  - trusted surface entries
  - demo loop entries
  - compatibility entries
  - workflow entries
  - next-action entries
  - custom-spec compatibility resolution

## Canonical Demo-Path Mapping

- Stable commands covered by this slice:
  - `bootstrap`
  - `diff-preview`
  - `context-basket`
  - `terminal`
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `apply-patch`
  - `reject-patch`
  - `persist`
  - `export-handoff`
- Canonical demo-path step advanced:
  - `preview and apply or reject a patch`
- Concrete blocker removed:
  - shim-backed terminal commands in the demo workflow previously inherited the base `terminal` spec flow step `export-handoff`, so follow-up metadata for apply/reject/persist was internally mislabeled even when the argv was correct. That made the CLI demo loop less deterministic for smoke checks and future A2UI/Console consumers reading command workflow contracts.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Verified the CLI contract path now rejects parser-surface drift while preserving canonical command ordering for the exposed command catalog.
2. Fixed lane-owned demo-loop resolution so workflow contracts preserve the logical demo token for apply/reject/persist instead of collapsing to `export-handoff`.
3. Updated regression coverage in the shared command-catalog unit tests to lock both parser-surface drift rejection and the corrected demo-path metadata.
4. Re-ran the required gate suite and refreshed the handoff metadata for re-review.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `python -m unittest tests.unit.test_commands_catalog -q`: `PASS`
- `python -m unittest tests.unit.test_diff_preview -q`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

### Risks / Blockers

- Risks:
  - this change is intentionally narrow and limited to command-contract metadata, but future command-surface expansion could regress parser-entrypoint invariants or logical flow-step labels if new shim-backed demo tokens are added without extending the same validation path and tests.
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): hardens command behavior for the active CLI smoke flow by keeping the demo workflow metadata deterministic.
- `ROADMAP.md` Milestone 2 (`Test Hardening`): adds focused regression coverage for the corrected command-contract metadata.
- `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the CLI-first command surface stable for the engine-first MVP loop.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete blocker removed on that step: shim-backed terminal workflow metadata no longer collapses `apply-patch`, `reject-patch`, and `persist` into `export-handoff`, and parser-surface drift on the exposed CLI contract now fails at validation time instead of silently leaving a stale operator-facing surface in place.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves a stable CLI command contract for the MVP loop and for future `Exegesis Console` consumption of the same engine/A2UI-facing command metadata.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
