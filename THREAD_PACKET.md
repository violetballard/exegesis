# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff refresh`
- Packet refresh basis: `updated on 2026-04-23 to align the handoff with the actual reviewed implementation slice called out by the reviewer packet`

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
  - `command_cli_contract()` now verifies that the canonical names implied by the CLI lookup table exactly match `command_names()`.
  - focused regression tests cover both the happy path and the catalog-drift failure case.

## Scope Completed

- Added a fail-closed guard in `command_cli_contract()` so the parser-facing CLI contract cannot silently diverge from the canonical command catalog ordering.
- Added regression coverage proving the CLI contract matches the catalog in the normal case and raises if catalog drift is introduced.
- Kept the slice narrow: one command-contract guard plus targeted tests, with no provider, routing, or broader workflow behavior changes.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `open project/document`.
- Concrete blocker removed: before this guard, the CLI-first MVP could ship a parser-facing command surface whose canonical-name order no longer matched the underlying command catalog, which makes the `open project/document` entry step vulnerable to migration drift between declared commands and the parser contract.
- Direct plan-alignment statement: this change makes `open project/document` more real by forcing the CLI contract used at the demo-path entrypoint to stay identical to the canonical catalog instead of letting catalog drift hide behind a passing lookup table.
- Why this is milestone-worthy now: `AGENTS.md` narrows active MVP work to engine stability, FTS-first retrieval, and A2UI contracts with CLI fallback; while Textual is disabled, a fail-closed guard on the CLI entry contract is part of keeping the active operator path trustworthy, not second-order cleanup.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval basis: shared test coverage is required to prove the contract guard and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `SCOPE_ALLOW_SHARED=1`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Re-anchored the handoff packet to the exact reviewed implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Added the required canonical demo-path mapping for the `open project/document` entry step and named the concrete contract-drift failure mode it prevents.
3. Narrowed the roadmap and vision mapping to CLI compatibility and canonical engine-contract evidence only.
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

- `ROADMAP.md` Milestone 3: user-facing output and operator contracts must be defined and locked intentionally.
- This diff contributes only the CLI-compatibility slice of that requirement by preventing migration drift in the parser-facing entry contract.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI is the active operator surface while interactive console work is deferred, so its canonical engine contract must stay deterministic.

### Routing / Provider Impact Note

- None. This diff only hardens local command-catalog validation and regression coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
