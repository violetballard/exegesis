# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff for reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` so it satisfies the high-risk AGENTS template and states exactly which canonical demo-path CLI step this Milestone 3 CLI-compatibility hardening change advances.
- Risk reason: the reviewed slice mixes lane-owned command code with a shared test file, and this fixer also updates shared handoff metadata to satisfy the lane-specific review gate.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff as a completed high-risk AGENTS packet pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Add the explicit canonical demo-path mapping statement the reviewer requested, keeping the claim pinned to the Milestone 3 CLI contract and the single demo-path step this slice directly hardens.
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
- First green tests: `make scope-check`, `./quality-format.sh --check`, and `./quality-lint.sh` passed during the rerun completed at `2026-04-23T21:18:21Z`.
- Before risky/shared file edit: this fixer edits shared handoff metadata only (`THREAD.md`, `THREAD_PACKET.md`).
- Ready for handoff: as of `2026-04-23T21:18:21Z`, the packet and required gate results match the reviewed slice.

## Review Basis

- Review scope remains pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed change summary:
  - `src/qual/commands/catalog.py`: routes `command_cli_contract()` through the stricter parser-surface validator so the contract must match both the canonical command order and the full declared CLI entrypoint surface.
  - `tests/unit/test_commands_catalog.py`: adds parser-surface drift regressions for dropped canonical tokens, alias substitution, alias reordering, extra accepted entrypoints, and removed expected aliases.
- This fixer pass does not change that implementation scope. It only regenerates the handoff metadata in `THREAD.md` and `THREAD_PACKET.md`.

## Scope Completed

- Regenerated the lane handoff as a completed high-risk AGENTS packet for the reviewed Milestone 3 CLI-compatibility hardening slice.
- Added the missing reviewer-requested canonical demo-path mapping statement and the explicit reason this work advances the Milestone 3 CLI loop directly instead of serving as generic infra cleanup.
- Kept review scope pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; no additional implementation change was made.
- Revalidated the branch tip with a fresh full gate rerun so the handoff reflects the actual final fixer state rather than the earlier packet-refresh timestamp.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `<=4` tasks, metadata-only fixer scope, `2` files changed by this fixer.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Plan Alignment

- Exact canonical demo-path step this reviewed slice makes more real:
  - direct step advanced: step 3 `preview and apply or reject a patch`
  - out of scope: no new step 1 `open project/document` or step 2 `retrieve relevant material` workflow coverage is claimed by this command-catalog contract slice
- Why this is direct MVP-loop work rather than second-order cleanup:
  - this is Milestone 3 CLI-compatibility hardening, not generic infra cleanup: it hardens the operator-visible command contract while Textual remains disabled and the CLI carries the demo path.
  - the reviewed `catalog.py` change makes the CLI contract fail fast if the parser-visible entrypoint surface drifts away from the command catalog, including alias-level drift that would otherwise still collapse to the same canonical tuple.
  - that stricter check protects the operator-visible patch preview/apply route, so deterministic CLI smoke coverage for the Milestone 3 command contract remains meaningful instead of silently testing the wrong contract.

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - `command_cli_contract()` now validates the actual declared parser surface, not only the deduplicated canonical-name projection, so alias-level parser drift fails fast.
- Required fix 2 satisfied:
  - targeted regressions in `tests/unit/test_commands_catalog.py` now cover concrete parser-surface drift cases such as dropped canonical tokens, alias substitution, entrypoint reordering, extra accepted aliases, and removed expected aliases.
- Required fix 3 satisfied:
  - this packet states explicitly which canonical demo-path step the change advances and why the work is direct Milestone 3 CLI-loop support.

## Canonical Demo-Path Mapping

- Primary step advanced directly: step 3 `preview and apply or reject a patch`
  - reason: the reviewed catalog contract check keeps the canonical CLI command surface aligned with the command catalog, so the patch preview/apply entrypoint cannot silently drift away from the route the operator and smoke tests expect.
- Canonical demo-path step(s) advanced:
  - step 3 `preview and apply or reject a patch`, because the CLI command contract now fails fast on parser/catalog drift instead of silently changing the operator-visible patch preview/apply surface while Textual remains disabled.
- Out of scope:
  - this slice does not claim new step 1 `open project/document` or step 2 `retrieve relevant material` workflow coverage.
- Explicit AGENTS mapping statement:
  - this reviewed change is not generic command-catalog cleanup. It is a Milestone 3 CLI-compatibility hardening change that makes step 3 `preview and apply or reject a patch` more real directly because it turns parser/catalog drift from a silent contract change into a deterministic failure on the exact CLI surface that step depends on.

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
2. Added the explicit canonical demo-path mapping statement showing that the reviewed deterministic command-contract change advances step 3 `preview and apply or reject a patch` directly.
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
- Verification timestamp: `2026-04-23T21:23:51Z`

### Risks / Blockers

- Risk: `HIGH`
- Remaining risk:
  - the lane remains high-risk because the reviewed slice includes one shared test file and this fixer updates shared handoff metadata.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 (`Product Readiness`): define and lock user-facing output contracts.
- `ROADMAP.md` MVP focus through `2026-05-04`: `feat-commands` is still an active implementation lane in the current engine-first push.

### Vision capability affected

- `PRODUCT_VISION.md` required capability 4 (`Operator-first control surface`): CLI remains a first-class surface for development and reliability.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
