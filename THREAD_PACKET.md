# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the Milestone 3 `feat-commands` operator surface deterministic at the `open project/document` step by preserving stable command-contract metadata and migration-safe command entrypoints while the Textual surface stays disabled.
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

- Hardened `command_cli_contract()` so it rejects catalog-entrypoint projection drift, including alias-only substitutions, token removals, token additions, and entrypoint reordering that would otherwise leave canonical command names unchanged.
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
  - `open project/document` via the `project-open` operator token
- Concrete Milestone / vision claim this supports:
  - `ROADMAP.md` Milestone 3 (`Product Readiness`) scope item `Define and lock user-facing output contracts`: this slice hardens deterministic CLI contract validation and migration-safe command entrypoints for the `project-open` operator token
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): CLI remains a first-class surface for development and reliability, so the `project-open` contract cannot be allowed to drift silently
- Concrete blocker removed:
  - This prevents parser/catalog drift from silently changing the CLI contract for the migration-safe `project-open` entrypoint used for `open project/document`.
- Scope guard:
  - this handoff is limited to deterministic CLI contract validation and migration-safe command entrypoints; it does not claim engine workflow behavior changes.
- Why this is not second-order work under the current narrowing rules:
  - the active operator surface is still the CLI while Textual stays disabled, so failing fast on parser/catalog drift and keeping the patch-review to apply/reject workflow tokens stable directly protects the live MVP command contract instead of adding optional catalog hygiene.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Verified the CLI contract path now rejects catalog-entrypoint projection drift while preserving canonical command ordering for the exposed command catalog.
2. Fixed lane-owned demo-loop resolution so workflow contracts preserve the logical demo token for apply/reject/persist instead of collapsing to `export-handoff`.
3. Canonicalized full demo-path argv back to the stable workflow token and updated regression coverage to lock both catalog-entrypoint projection drift rejection and the corrected demo-path metadata.
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

- `ROADMAP.md` Milestone 3 (`Product Readiness`) scope item `Define and lock user-facing output contracts`: this handoff keeps the `project-open` CLI contract deterministic and migration-safe.
- `ROADMAP.md` active MVP emphasis `feat-commands`: keeps deterministic CLI contract validation in the lane-owned command catalog without broadening into engine workflow behavior claims.
- Canonical demo-path step advanced: `open project/document` via the `project-open` operator token.
- Concrete blocker removed on that step: this prevents parser/catalog drift from silently changing the CLI contract for the migration-safe `project-open` entrypoint used for `open project/document`.
- Scope guard: this handoff is limited to deterministic CLI contract validation and migration-safe command entrypoints; it does not claim engine workflow behavior changes.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): preserves the required CLI compatibility for `open project/document` and the rest of the MVP loop while `Exegesis Console` remains disabled and CLI remains the first-class operator surface.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
