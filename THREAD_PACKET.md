# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff for reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` so it satisfies the high-risk AGENTS template, states exactly which canonical demo-path CLI step this canonical command order/name hardening change advances, and avoids broader parser-surface claims the reviewed slice does not prove.
- Risk reason: the reviewed slice mixes lane-owned command code with a shared test file, and this fixer also updates shared handoff metadata to satisfy the lane-specific review gate.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff as a completed high-risk AGENTS packet pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Add the explicit canonical demo-path mapping statement the reviewer requested, keeping the claim pinned to the Milestone 3 CLI contract and the single demo-path step this reviewed canonical-order/name slice directly hardens.
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
- First green tests: `make scope-check`, `./quality-format.sh --check`, and `./quality-lint.sh` passed during the rerun completed at `2026-04-23T21:59:30Z`.
- Before risky/shared file edit: this fixer edits shared handoff metadata only (`THREAD.md`, `THREAD_PACKET.md`).
- Ready for handoff: as of `2026-04-23T21:59:30Z`, the packet and required gate results match the reviewed slice.

## Review Basis

- Review scope remains pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed change summary:
  - `src/qual/commands/catalog.py`: makes `command_cli_contract()` fail if the canonical command order derived from `command_cli_lookup_table()` no longer matches `command_names()`.
  - `tests/unit/test_commands_catalog.py`: adds the targeted mismatch regression that proves the contract rejects canonical-name/order drift in that catalog projection.
- This fixer pass does not change that implementation scope. It only regenerates the handoff metadata in `THREAD.md` and `THREAD_PACKET.md`.

## Scope Completed

- Regenerated the lane handoff as a completed high-risk AGENTS packet for the reviewed Milestone 3 CLI-compatibility hardening slice.
- Added the missing reviewer-requested explicit sentence naming the canonical demo-path step and the reason this reviewed canonical-order/name hardening advances the Milestone 3 CLI-first MVP loop directly instead of serving as generic infra cleanup.
- Kept review scope pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; no additional implementation change was made.
- Revalidated the branch tip with a fresh full gate rerun so the handoff reflects the actual final fixer state rather than the earlier packet-refresh timestamp.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `<=4` tasks, metadata-only fixer scope, `2` files changed by this fixer.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Plan Alignment

- Operator-path mapping this reviewed slice advances:
  - this hardens the stable CLI command surface the operator uses to invoke the engine-first loop while Textual remains disabled, including the command routes used to open a project or document, retrieve relevant material, preview or apply a patch, and hand work off through the existing CLI contract.
  - the direct step strengthened by the reviewed change is `preview and apply or reject a patch`: `command_cli_contract()` now fails fast if canonical command order or canonical command names drift away from the catalog the patch route depends on.
  - out of scope: this slice does not claim new workflow implementation for opening, retrieval, or export; it keeps those existing CLI entrypoints deterministic by preventing silent parser or catalog drift in the shared command contract.
- Why this is direct MVP-loop work rather than second-order cleanup:
  - this is operator-surface hardening, not generic catalog cleanup: the reviewed change keeps the CLI loop invocable and deterministic on the same contract the operator and smoke tests rely on while Textual remains disabled.
  - the reviewed `catalog.py` change makes the CLI contract fail fast if the canonical command order derived from the lookup table drifts away from `command_names()`.
  - that check protects the operator-visible patch preview/apply route specifically and preserves trust in the broader CLI control surface generally, so deterministic smoke coverage cannot silently validate the wrong command ordering.

## Canonical Demo-Path Step Advanced

- AGENTS-required explicit step statement:
  - this change directly strengthens `preview and apply or reject a patch` in the canonical demo path because `command_cli_contract()` now fails fast when canonical command order or canonical command names drift away from the catalog the operator-facing patch route depends on while Textual remains disabled.
- Why this is the primary step:
  - the reviewed slice does not add new workflow behavior; it makes the existing patch preview/apply CLI route deterministic and smoke-testable by turning parser or catalog drift into an immediate contract failure.

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - this packet now includes an explicit sentence naming demo-path step 3 `preview and apply or reject a patch` and explaining that the reviewed contract hardening keeps that CLI route aligned with the catalog order and canonical command names the operator and smoke tests expect.
- Required fix 2 satisfied:
  - the scope language is now pinned to the reviewed behavior only: canonical command order and canonical-name consistency between `command_cli_lookup_table()` and `command_names()`.
- Required fix 3 satisfied:
  - the handoff body preserves both corrections so the roadmap and vision mapping is unambiguous on its own.

## Canonical Demo-Path Mapping

- Operator terms:
  - this hardens the stable CLI control surface used to reach `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and existing CLI handoff or export flows without silent parser or catalog drift.
- Primary direct step advanced:
  - `preview and apply or reject a patch`
  - reason: the reviewed catalog contract check keeps canonical command order and canonical command names aligned with the command catalog, so the patch preview/apply entrypoint cannot silently drift away from the route the operator and smoke tests expect.
- Explicit step sentence:
  - this change directly strengthens `preview and apply or reject a patch` in the CLI-first MVP loop because it turns canonical command order or canonical-name drift into a deterministic failure on the exact CLI surface the operator-facing patch route depends on while Textual remains disabled.
- Out of scope:
  - this slice does not claim new workflow implementation for `open project/document`, `retrieve relevant material`, or export; it preserves determinism for those existing CLI routes by protecting the shared command contract they all consume.
- Explicit AGENTS mapping statement:
  - this reviewed change is not generic command-catalog cleanup. It is stable CLI control-surface hardening for the active engine-first demo path, with direct impact on `preview and apply or reject a patch` and protective impact on the rest of the invocable CLI loop.

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
- Approval provenance:
  - the reviewed shared-test edit is covered by the repo's recorded lane-specific shared-test allowlist in `scripts/scope-check.sh`, where `is_approved_shared_test()` explicitly approves `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`.
  - verification basis: `make scope-check` passes from this branch with that recorded allowlist in effect, so the exception is traceable to repo policy rather than an uncited packet claim.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Regenerated the handoff as a completed high-risk AGENTS packet for reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Added the explicit canonical demo-path mapping statement showing that the reviewed canonical-order/name contract change advances step 3 `preview and apply or reject a patch` directly.
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
- Verification timestamp: `2026-04-23T21:59:30Z`

### Risks / Blockers

- Risk: `HIGH`
- Remaining risk:
  - the lane remains high-risk because the reviewed slice includes one shared test file and this fixer updates shared handoff metadata.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`): command and diff-preview behavior hardening while the manual CLI smoke flow stays stable.
- `ROADMAP.md` Milestone 2 (`Test Hardening`): focused command-contract regression coverage for parser and catalog drift.
- `ROADMAP.md` MVP focus through `2026-05-04`: `feat-commands` remains an active implementation lane in the current engine-first push.

### Vision capability affected

- `PRODUCT_VISION.md` required capability 4 (`Operator-first control surface`): CLI remains a first-class surface for development and reliability.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
