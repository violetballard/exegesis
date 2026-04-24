# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix verification refresh`
- Packet refresh basis: `updated on 2026-04-23 to confirm the branch tip satisfies the reviewer's parser-surface drift fixes and to align the handoff text with the actual reviewed implementation slice`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the CLI contract so the parser-facing command catalog stays in lockstep with the canonical command catalog used by the CLI-first MVP loop.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Re-anchor the handoff to the exact reviewed implementation slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Add the AGENTS-required canonical demo-path statement naming the exact step advanced and the concrete blocker removed.
3. Tighten roadmap and product-vision mapping to only the CLI compatibility evidence this diff actually proves.
4. Rerun the required gates and refresh the compatibility pointer file.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` now validates the full parser-facing CLI entrypoint projection against the declared catalog surface instead of checking only the deduplicated canonical-name projection.
  - focused regression tests cover canonical-name alignment and parser-surface drift failures, including dropped canonical tokens, removed aliases, and reordered parser entrypoints.

## Scope Completed

- Added a fail-closed guard in `command_cli_contract()` so the parser-facing CLI contract cannot silently diverge from the canonical command catalog ordering.
- Added regression coverage proving the CLI contract matches the catalog in the normal case and raises if parser-surface drift is introduced.
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

1. Re-anchored the handoff packet to the exact reviewed implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Added the required canonical demo-path mapping for the CLI fallback `open project/document` entry step and named the concrete parser-surface drift failure mode it prevents.
3. Tightened the roadmap and vision mapping to the actual Milestone 3 CLI-compatibility requirement and canonical engine-contract evidence only.
4. Refreshed the compatibility pointer file and reran the required gates.

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
