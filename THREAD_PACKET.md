# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the active CLI-first MVP operator surface deterministic at the `open project/document` step, and across the broader CLI MVP loop, by preserving stable command-contract metadata while the Textual surface stays disabled.
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

- Reviewed implementation base previously approved for comparison: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewed implementation commits included in this re-review:
  - `06540160de4cf0d452c1ed9b4d4926c205888be9` (`fix(commands): preserve demo flow steps for shim tokens`)
  - `7fe699292035b6671bd17a3c5defa1659819c6fa` (`feat(commands): canonicalize demo argv workflow tokens`)
- Current handoff packet is a metadata-only refresh on top of that reviewed implementation range
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Scope Completed

- Hardened `command_cli_contract()` so it rejects parser-surface drift, including alias-only substitutions, token removals, token additions, and entrypoint reordering that would otherwise leave canonical command names unchanged.
- Fixed `_resolve_demo_loop_token()` so demo-loop resolution preserves the logical demo token as the flow step when a shim-backed terminal command is selected for `apply-patch`, `reject-patch`, or `persist`.
- Added canonical demo-argv normalization so shim-backed parser invocations map back to the stable workflow token used by the demo-path contracts.
- Kept the active CLI smoke route self-describing from `patch-review` into `apply-patch` or `reject-patch`, then `persist`, by preventing shim-backed terminal actions from collapsing back to fallback `terminal` metadata.
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
  - `open project/document`
- Broader CLI operator surface kept stable:
  - `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`
- Concrete blocker removed:
  - parser/catalog drift and shim-backed fallback metadata could silently destabilize the operator-facing CLI entrypoints that the engine-side MVP loop still depends on while Textual stays disabled. This slice keeps the command contract deterministic so `project-open` and the downstream CLI workflow tokens remain explicit instead of drifting behind unchanged canonical command names.
- Why this is not second-order work under the current narrowing rules:
  - the active operator surface is still the CLI while Textual stays disabled, so failing fast on parser/catalog drift and keeping the patch-review to apply/reject workflow tokens stable directly protects the live MVP command contract instead of adding optional catalog hygiene.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Verified the CLI contract path now rejects parser-surface drift while preserving canonical command ordering for the exposed command catalog.
2. Fixed lane-owned demo-loop resolution so workflow contracts preserve the logical demo token for apply/reject/persist instead of collapsing to `export-handoff`.
3. Canonicalized full demo-path argv back to the stable workflow token and updated regression coverage to lock both parser-surface drift rejection and the corrected demo-path metadata.
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

- `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): hardens the `open project/document` entrypoint and the broader CLI smoke flow by keeping the command workflow metadata deterministic.
- `ROADMAP.md` Milestone 2 (`Test Hardening`): adds focused regression coverage for the corrected command-contract metadata.
- `ROADMAP.md` active MVP emphasis `feat-commands`: keeps the CLI-first command surface stable for the engine-first MVP loop.
- Canonical demo-path step advanced: `open project/document`.
- Canonical smoke-route coverage kept explicit: `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`.
- Concrete blocker removed on that step: parser-surface drift on the exposed CLI contract now fails at validation time instead of silently leaving stale operator entrypoints in place, and the downstream shim-backed workflow tokens remain explicit for the rest of the CLI MVP loop.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves a stable CLI operator surface for `open project/document` and the rest of the MVP loop while `Exegesis Console` remains disabled.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
