# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff for reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` so it satisfies the high-risk AGENTS template and states exactly which canonical demo-path CLI step(s) this command-contract change advances.
- Risk reason: the reviewed slice mixes lane-owned command code with a shared test file, and this fixer also updates shared handoff metadata to satisfy the lane-specific review gate.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff as a completed high-risk AGENTS packet pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Add the explicit canonical demo-path mapping statement the reviewer requested, including why this is direct MVP-loop support rather than second-order cleanup.
3. Keep implementation scope pinned to the reviewed files and record the shared-file basis truthfully.
4. Run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, then stamp the packet with the results.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: packet scope reset to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` instead of the full branch tip.
- First green tests: `make scope-check`, `./quality-format.sh --check`, and `./quality-lint.sh` passed during the rerun completed at `2026-04-23T20:50:17Z`.
- Before risky/shared file edit: this fixer edits shared handoff metadata only (`THREAD.md`, `THREAD_PACKET.md`).
- Ready for handoff: as of `2026-04-23T20:50:17Z`, the packet and required gate results match the reviewed slice.

## Review Basis

- Review scope remains pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed change summary:
  - `src/qual/commands/catalog.py`: adds a strict `command_cli_contract()` consistency check so canonical CLI names must match catalog order instead of silently drifting.
  - `tests/unit/test_commands_catalog.py`: adds regression coverage that proves the CLI contract matches catalog order and raises on catalog drift.
- This fixer pass does not change that implementation scope. It only regenerates the handoff metadata in `THREAD.md` and `THREAD_PACKET.md`.

## Scope Completed

- Regenerated the lane handoff as a completed high-risk AGENTS packet for the reviewed shared-file slice.
- Added the missing reviewer-requested canonical demo-path mapping statement and the explicit reason this work advances the MVP loop directly.
- Kept review scope pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; no additional implementation change was made.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `<=4` tasks, metadata-only fixer scope, `2` files changed by this fixer.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Plan Alignment

- Exact canonical demo-path steps this reviewed slice makes more real:
  - direct step advanced: step 2 `retrieve relevant material`
  - immediate follow-on step hardened: step 3 `preview and apply or reject a patch`
  - out of scope: no new step 1 `open project/document` workflow coverage is claimed beyond preserving the existing CLI entrypoint into retrieval
- Why this is direct MVP-loop work rather than second-order cleanup:
  - the reviewed `catalog.py` change makes the CLI contract fail fast if parser-visible canonical command names drift away from the command catalog order.
  - that drift check protects the operator-visible command route used to reach retrieval and the immediate preview/apply follow-on, so deterministic CLI smoke coverage remains meaningful instead of silently testing the wrong contract.

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - this packet now includes the completed high-risk AGENTS fields that were missing: `Risk reason`, `Planned Tasks`, `Early Review Triggers`, `Stop Triggers`, and `Checkpoint Cadence`.
- Required fix 2 satisfied:
  - this packet now states exactly which canonical demo-path step(s) the reviewed deterministic command-contract change advances and why that is direct MVP-loop support.
- Required fix 3 satisfied:
  - review scope remains pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and no implementation change beyond handoff metadata regeneration was made in this fixer pass.

## Canonical Demo-Path Mapping

- Primary step advanced directly: step 2 `retrieve relevant material`
  - reason: the reviewed catalog contract check keeps the canonical CLI command surface aligned with the command catalog, so the retrieval entrypoint cannot silently drift away from the route the operator and smoke tests expect.
- Immediate dependent step hardened: step 3 `preview and apply or reject a patch`
  - reason: the same deterministic CLI contract is what keeps the next operator-visible command path stable after retrieval, so the review/apply follow-on remains reachable through the intended CLI contract.
- Out of scope:
  - this slice does not claim new step 1 `open project/document` workflow coverage beyond preserving the existing CLI entrypoint into retrieval.
- Explicit AGENTS mapping statement:
  - this reviewed change is not generic command-catalog cleanup. It makes step 2 more real directly, and step 3 more real as the immediate follow-on, because it turns parser/catalog drift from a silent contract change into a deterministic failure on the exact CLI surface the MVP loop depends on.

## Shared-Path Approval Basis

- Lane-owned implementation in the reviewed slice:
  - `src/qual/commands/catalog.py`
- Shared file in the reviewed slice:
  - `tests/unit/test_commands_catalog.py`
- Shared files updated by this fixer for handoff accuracy:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Shared-file note:
  - this packet claims high-risk/shared-file handling because the reviewed commit includes a shared test file and this fixer updates shared handoff metadata. No integrator-locked runtime files were changed.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Regenerated the handoff as a completed high-risk AGENTS packet for reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Added the explicit canonical demo-path mapping statement showing that the reviewed deterministic command-contract change advances step 2 directly and step 3 as the immediate follow-on.
3. Kept implementation scope pinned to the reviewed files and recorded the shared-file basis truthfully.
4. Re-ran the required gate suite and recorded the results below.

### Files Changed

- Reviewed implementation files at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:
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
- Verification timestamp: `2026-04-23T20:50:17Z`

### Risks / Blockers

- Risk: `HIGH`
- Remaining risk:
  - the lane remains high-risk because the reviewed slice includes one shared test file and this fixer updates shared handoff metadata.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 (`Product Readiness`): define and lock user-facing output contracts.
- `ROADMAP.md` Milestone 5 (`A2UI Presentation Layer`): keep CLI fallback views and the MVP CLI loop executable against the same engine contracts while UI work remains deferred.
- `ROADMAP.md` MVP focus through `2026-05-04`: `feat-commands` is still an active implementation lane in the current engine-first push.

### Vision capability affected

- `PRODUCT_VISION.md` required capability 4 (`Operator-first control surface`): CLI remains a first-class surface for development and reliability.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
