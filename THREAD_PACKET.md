# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `538095c47a6bc5f971e9811b83745571915e4268`
- Packet refresh role: `reviewer-fix handoff refresh`
- Packet refresh basis: `updated on 2026-04-23 after adding the explicit diff parser-surface regression and revalidating the required gates`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the CLI contract so the parser-facing command catalog stays in lockstep with the canonical command catalog used by the CLI-first MVP loop, including fail-closed rejection when the `diff` parser token disappears from the approved surface.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Tighten the command contract wording and helper structure so the full declared parser surface remains the explicit validation target.
2. Add a regression that proves the contract fails when the `diff` parser token disappears from the accepted surface.
3. Refresh the AGENTS-required canonical demo-path statement naming the exact step advanced and the concrete blocker removed.
4. Rerun the required gates and refresh the compatibility pointer file.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `538095c47a6bc5f971e9811b83745571915e4268` (`test(commands): cover diff parser surface drift`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` keeps the full parser-facing CLI entrypoint projection as the explicit validation target through a dedicated declared-entrypoint projection helper instead of relying on the deduplicated canonical-name projection.
  - focused regression tests now include the exact reviewer-called failure mode: the contract raises when the `diff` parser token disappears from the accepted `diff-preview` surface, alongside the broader canonical-name and parser-order drift cases.

## Scope Completed

- Added a fail-closed guard in `command_cli_contract()` so the parser-facing CLI contract cannot silently diverge from the canonical command catalog ordering.
- Added regression coverage proving the CLI contract matches the catalog in the normal case and raises if parser-surface drift is introduced, including explicit rejection when the `diff` parser token disappears.
- Kept the slice narrow: one command-contract guard plus targeted tests, with no provider, routing, or broader workflow behavior changes.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `open project/document`.
- Active MVP operator path strengthened: the CLI fallback path for `open project/document` while Textual remains disabled.
- Concrete blocker removed: before this guard, the CLI-first MVP could lose required parser tokens or aliases such as `diff` while the deduplicated canonical-name tuple still matched `command_names()`, which left the `open project/document` entry step and the rest of the CLI loop vulnerable to silent parser-surface drift during the migration.
- Direct plan-alignment statement: this change makes the CLI fallback `open project/document` entry step more real by forcing that demo-path entrypoint to fail closed whenever the parser-facing token surface and canonical command catalog stop matching.
- Scope-tightening note: this handoff claims only the CLI fallback entry step above; it does not claim to harden patch preview, apply/reject, or any broader command flow in this slice.
- Why this is milestone-worthy now instead of second-order cleanup: `AGENTS.md` says contract work counts only when it removes a concrete blocker on the canonical demo path. This guard does that because Milestone 3 still relies on the CLI as the active operator surface while Textual is disabled, so preventing silent contract drift at the first demo-path step hardens the live CLI-first MVP loop, not a speculative future path.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval basis: shared test coverage is required to prove the contract guard and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `SCOPE_ALLOW_SHARED=1`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Re-anchored the handoff packet to the exact reviewed implementation commit `538095c47a6bc5f971e9811b83745571915e4268`.
2. Kept the command-contract validation pinned to the full declared parser surface and named that surface explicitly in the implementation.
3. Added the reviewer-requested regression proving the contract fails when the `diff` parser token disappears from the accepted `diff-preview` surface.
4. Refreshed the canonical demo-path mapping, compatibility pointer, and required gate results for the CLI-first MVP loop.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`
- `THREAD.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

### Risks / Blockers

- Risks:
  - future command additions still need regression coverage so the CLI contract keeps failing closed when parser/catalog drift is introduced
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3: preserve CLI compatibility while the package/layout migration lands.
- This diff contributes only the Milestone 3 CLI-compatibility and migration-safe-entrypoint slice by ensuring the active CLI-first MVP loop can start with a stable `open project/document` contract instead of letting parser-surface tokens drift away from the canonical command catalog.

### Vision capability affected

- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the CLI is the active operator surface while Textual remains disabled, so its engine-facing contract and CLI compatibility need to stay deterministic and migration-safe enough to drive the demo path now.

### Routing / Provider Impact Note

- None. This diff only hardens local command-catalog validation and regression coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
