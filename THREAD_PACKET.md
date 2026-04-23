# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the handoff so it matches the current fixed branch state, states exactly which canonical demo-path CLI step this parser-surface contract hardening advances, and records the concrete engine-first MVP blocker removed by the token-surface drift checks.
- Risk reason: the fixed slice mixes lane-owned command code with a shared test file, and this fixer also updates shared handoff metadata to satisfy the lane-specific review gate.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff as a completed high-risk AGENTS packet for the current fixed branch state.
2. Add the explicit canonical demo-path mapping statement the reviewer requested, tying the claim to the Milestone 3 CLI contract and the single demo-path step this parser-surface slice directly hardens.
3. Keep implementation scope pinned to the fixed command-catalog files and record the shared-file basis truthfully.
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

- Plan complete: packet scope reset to the current fixed branch state instead of the earlier narrower review slice.
- First green tests: `make scope-check`, `./quality-format.sh --check`, and `./quality-lint.sh` passed during the rerun completed at `2026-04-23T22:16:13Z`.
- Before risky/shared file edit: this fixer edits shared handoff metadata only (`THREAD.md`, `THREAD_PACKET.md`).
- Ready for handoff: as of `2026-04-23T22:16:13Z`, the packet and required gate results match the fixed branch state.

## Review Basis

- Review scope covers the current fixed branch state for the command CLI contract.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed change summary:
  - `src/qual/commands/catalog.py`: makes `command_cli_contract()` fail if the declared parser surface drifts from the approved catalog, including token add, remove, alias substitution, or reorder changes that leave canonical command names unchanged.
  - `tests/unit/test_commands_catalog.py`: adds targeted regressions proving the contract rejects dropped canonical tokens, reordered accepted entrypoints, removed aliases, and other token-surface drift cases.
- This fixer pass does not change that implementation scope. It regenerates the handoff metadata in `THREAD.md` and `THREAD_PACKET.md` so the packet matches the fixed branch state.

## Scope Completed

- Regenerated the lane handoff as a completed high-risk AGENTS packet for the fixed Milestone 3 CLI-compatibility hardening slice.
- Added the missing reviewer-requested explicit sentence naming the canonical demo-path step and the concrete blocker removed from the engine-first MVP loop.
- Kept implementation scope pinned to the command-catalog files already carrying the code-side reviewer fixes; this fixer changes only handoff metadata.
- Revalidated the branch tip with a fresh full gate rerun so the handoff reflects the actual final fixer state rather than the earlier packet-refresh timestamp.

## Kickoff Budget / Limits Compliance

- High-risk budget honored: `<=4` tasks, metadata-only fixer scope, `2` files changed by this fixer.
- Files edited by this fixer:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Plan Alignment

- Operator-path mapping this fixed slice advances:
  - this hardens the stable CLI command surface the operator uses to invoke the engine-first loop while Textual remains disabled, including the command routes used to open a project or document, retrieve relevant material, preview and apply or reject a patch, and hand work off through the existing CLI contract.
  - the canonical demo-path step this work makes more real is `preview and apply or reject a patch`.
  - the direct step strengthened by the fixed change is `preview and apply or reject a patch`: `command_cli_contract()` now fails fast if the accepted CLI token surface for that route drifts away from the catalog the patch-review route depends on.
  - out of scope: this slice does not claim new workflow implementation for opening, retrieval, or export; it keeps those existing CLI entrypoints deterministic by preventing silent parser or catalog drift in the shared command contract.
- Why this is direct MVP-loop work rather than second-order cleanup:
  - this is operator-surface hardening, not generic catalog cleanup: the fixed change keeps the CLI patch-review step invocable and deterministic on the same contract the operator and smoke tests rely on while Textual remains disabled.
  - the fixed `catalog.py` change makes the CLI contract fail fast if accepted parser tokens drift away from the declared catalog surface, not just when canonical command names diverge.
  - that check removes the concrete blocker where the operator-visible patch-review route could silently lose or reorder accepted tokens while still resolving to the same canonical command, making `preview and apply or reject a patch` unreliable even though the command name tuple still looked healthy.

## Canonical Demo-Path Step Advanced

- AGENTS-required explicit step statement:
  - the canonical demo-path step advanced by this work is `preview and apply or reject a patch`.
  - this change directly strengthens `preview and apply or reject a patch` in the canonical demo path because `command_cli_contract()` now fails fast when the accepted CLI token surface for that route drifts away from the approved catalog the patch-review route depends on while Textual remains disabled.
- Why this is the primary step:
  - the slice does not add new workflow behavior; it makes the existing patch preview/apply CLI route deterministic and smoke-testable by turning parser-surface drift into an immediate contract failure on the operator path that performs patch review.

## Reviewer Fix Closure

- Required fix 1 satisfied:
  - `src/qual/commands/catalog.py` now validates the full intended parser surface, and this packet states that behavior precisely instead of describing only canonical-name alignment.
- Required fix 2 satisfied:
  - `tests/unit/test_commands_catalog.py` includes token-surface drift regressions, including dropped canonical-token and reordered-entrypoint cases that would keep canonical command names unchanged.
- Required fix 3 satisfied:
  - the handoff body names the exact canonical demo-path step advanced and the concrete blocker removed from the engine-first CLI loop.
- Required fix 4 satisfied:
  - the packet claim language now matches the code precisely: full parser-surface drift rejection, not just canonical command alignment.

## Canonical Demo-Path Mapping

- Operator terms:
  - this hardens the stable CLI control surface used to reach `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and existing CLI handoff or export flows without silent parser or catalog drift.
- Primary direct step advanced:
  - `preview and apply or reject a patch`
  - reason: the fixed catalog contract check keeps the accepted parser tokens for the patch preview/apply route aligned with the command catalog, so that entrypoint cannot silently drop, swap, or reorder accepted tokens while still resolving to the same canonical command.
- Explicit step sentence:
  - this change directly strengthens `preview and apply or reject a patch` in the CLI-first MVP loop because it turns token-surface drift into a deterministic failure on the exact CLI surface the operator-facing patch-review route depends on while Textual remains disabled.
- Out of scope:
  - this slice does not claim new workflow implementation for `open project/document`, `retrieve relevant material`, or export; it preserves determinism for those existing CLI routes by protecting the shared command contract they all consume.
- Explicit AGENTS mapping statement:
  - this reviewed change is not generic command-catalog cleanup. It is stable CLI control-surface hardening for the active engine-first demo path, with direct impact on `preview and apply or reject a patch`.
- Concrete blocker removed:
  - before this fix set, the patch-review route could have silently lost or reordered accepted CLI tokens without tripping the canonical command-name tuple. The branch now rejects that drift immediately, so the CLI-first MVP loop cannot present a stale parser surface for `preview and apply or reject a patch` while still appearing catalog-consistent.

## Shared-Path Approval Basis

- Lane-owned implementation in the fixed slice:
  - `src/qual/commands/catalog.py`
- Shared file in the fixed slice:
  - `tests/unit/test_commands_catalog.py`
- Shared files updated by this fixer for handoff accuracy:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Shared-file note:
  - this packet claims high-risk/shared-file handling because the fixed branch state includes a shared test file and this fixer updates shared handoff metadata. No integrator-locked runtime files were changed.
- Approval provenance:
  - the reviewed shared-test edit is covered by the repo's recorded lane-specific shared-test allowlist in `scripts/scope-check.sh`, where `is_approved_shared_test()` explicitly approves `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`.
  - verification basis: `make scope-check` passes from this branch with that recorded allowlist in effect, so the exception is traceable to repo policy rather than an uncited packet claim.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Regenerated the handoff as a completed high-risk AGENTS packet for the current fixed branch state.
2. Added the explicit canonical demo-path mapping statement showing that the parser-surface contract change advances step 5 `preview and apply or reject a patch` directly and removes the silent token-drift blocker on that route.
3. Kept implementation scope pinned to the fixed command-catalog files and recorded the shared-file basis truthfully.
4. Re-ran the required gate suite and recorded the results below.

### Files Changed

- Implementation files carrying the fixed behavior:
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
- Verification timestamp: `2026-04-23T22:16:13Z`

### Risks / Blockers

- Risk: `HIGH`
- Remaining risk:
  - the lane remains high-risk because the fixed slice includes one shared test file and this fixer updates shared handoff metadata.
- Blockers:
  - none.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 (`Real workflow loop`): this is CLI-compatibility hardening for the active MVP loop because the CLI must still execute the demo path while Textual remains disabled, and the patch-review step only stays operator-safe when the accepted CLI token surface for `preview and apply or reject a patch` remains explicit, intentional, and testable instead of silently drifting under the same canonical command name.
- `ROADMAP.md` active lane `feat-commands`: scope remains limited to CLI compatibility and migration-safe entrypoints in `src/qual/commands/**`; this packet does not claim generic workflow or audit progress beyond that operator path.

### Vision capability affected

- `PRODUCT_VISION.md` required capability 3 (`Canonical engine contract`): the future Textual client depends on one clean engine-facing state and action surface, and this slice keeps the current CLI compatibility layer stable by turning silent parser-surface drift into an immediate contract failure on the exact patch-review route the MVP loop uses while Textual remains disabled.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.
