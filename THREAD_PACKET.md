# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff packet so it matches the already-fixed command-catalog branch state, names the exact canonical CLI steps the contract hardening protects, and maps the change to the current repo roadmap and product-vision language.
- Risk reason: the reviewed implementation includes one approved shared test file, and this fixer refreshes shared handoff metadata for re-review.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff packet around the current fixed branch state.
2. Add the exact canonical CLI-step mapping the reviewer requested.
3. Tighten roadmap and product-vision claims so they match the actual diff.
4. Re-run the required gate suite and record the results.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: handoff scope reset to the current fixed command-catalog implementation plus metadata refresh only.
- First green tests: recorded below from the final rerun in this fixer pass.
- Before risky/shared file edit: this fixer only updates shared handoff metadata; no new runtime shared-file edits are introduced.
- Ready for handoff: packet and gate results now match the current branch state.

## Review Basis

- Review scope covers the current fixed branch state for the command CLI contract.
- Reviewed implementation commit pinned for re-review: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Metadata-only packet refresh commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are out of implementation review scope unless a regenerated handoff explicitly broadens the review basis.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Scope Completed

- Kept the implementation review basis pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Regenerated the handoff packet so it states the exact canonical CLI flow steps protected by the contract hardening: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Tightened roadmap and product-vision mapping to the current repo documents and removed stale claims that were not supported by the actual diff.
- Re-ran the required gate suite and recorded the outcomes below.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `4` tasks, metadata-only fixer scope.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - the packet now names the exact canonical CLI steps advanced by this work: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Required fix 2 satisfied:
  - roadmap and vision mapping now matches the actual diff and the current repo documents.
- Required fix 3 satisfied:
  - review basis remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and this fixer bundles no new implementation scope.

## Canonical CLI Step Mapping

- Exact canonical CLI steps this change advances:
  - `project-open`
  - `retrieval`
  - `patch-review`
  - `export-handoff`
- Why these are the right steps:
  - `src/qual/commands/catalog.py` defines those canonical flow steps and the accepted CLI token surface for each command path.
  - `command_cli_contract()` now validates that the parser surface still matches the approved catalog instead of only checking canonical command names.
  - `tests/unit/test_commands_catalog.py` adds regressions that fail on dropped tokens, removed aliases, or reordered entrypoints even when canonical names still match.
- Concrete operator-facing effect:
  - the CLI surface for the canonical command flow now fails fast on parser drift instead of silently presenting a stale or reordered token surface to operators and smoke tests.
- Out of scope:
  - this slice does not add new command behavior, new flags, or new workflow implementation beyond contract hardening and focused regression coverage.

## Shared-Path Approval Basis

- Lane-owned implementation in the reviewed scope:
  - `src/qual/commands/catalog.py`
- Approved shared file in the reviewed scope:
  - `tests/unit/test_commands_catalog.py`
- Shared metadata files changed by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Regenerated the handoff packet around the current fixed branch state.
2. Added the exact canonical CLI-step mapping for the contract hardening.
3. Tightened roadmap and product-vision claims to match the actual diff and current repo docs.
4. Re-ran the required gate suite and recorded the results.

### Files Changed

- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata files changed by this fixer:
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

- Risk: `HIGH`
- Remaining risk:
  - the handoff remains high-risk because the reviewed branch state includes one approved shared regression file.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 2 (`Test Hardening`): this adds targeted parser-edge regressions identified during review.
- `ROADMAP.md` Milestone 3 (`Product Readiness`): this hardens an intentional user-facing command contract by rejecting parser-surface drift on the canonical CLI flow.
- `ROADMAP.md` active MVP emphasis `feat-commands`: this keeps the CLI command surface deterministic while that lane remains active.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): the CLI remains a first-class operator surface, and this change keeps that surface deterministic by making parser drift fail fast.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
