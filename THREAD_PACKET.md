# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the CLI-first MVP command surface deterministic and parser-ready at the current branch tip so the operator-facing command entry contract stays stable during the Milestone 3 migration.
- Risk reason: the validated slice includes the approved shared test `tests/unit/test_commands_catalog.py`, so this handoff uses the high-risk template even though implementation stays command-surface-only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Refresh the handoff packet so it satisfies the required high-risk AGENTS structure.
2. State the exact canonical demo-path step this command-surface work advances.
3. Tighten roadmap and product-vision mapping to the actual CLI compatibility diff.
4. Re-run the required local gates and record outcomes for re-review.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: packet-only reviewer fixes identified; no implementation defect found in the reviewer packet.
- First green tests: satisfied by the full gate rerun recorded below.
- Before risky/shared file edit: approved shared-test exception carried forward for `tests/unit/test_commands_catalog.py`; this fixer refresh does not add new shared implementation paths.
- Ready for handoff: satisfied by this refreshed packet plus the full gate rerun recorded below.

## Packet Traceability Note

- This fixer refresh is anchored to pre-fix branch tip `72c9180992b2c45c7776dfc2155ecfecb39c9bfe`.
- Implementation commits in scope:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - lock `command_cli_contract()` to canonical catalog ordering.
  - `802b61876fff8125fb7f2af16e2f951219eee546` - tighten demo workflow preferred commands.
  - `7991f9b7227646da8922964106315a0c9afe7382` - normalize demo command compatibility variants.
- Reviewer-fix scope in this refresh: keep the high-risk handoff structure explicit, preserve the concrete demo-path mapping, and narrow the claims to existing MVP-loop command-contract hardening only.

## Reviewer Required Fixes Satisfied

1. Added the explicit canonical demo-path mapping for this slice: it strengthens the `open project/document` step by keeping the CLI entry contract deterministic while Textual remains disabled.
2. Tightened the product-vision mapping so the handoff claims `Canonical engine contract` only, without claiming `Auditable state and workflow`.
3. Kept the packet scope language narrow to command-catalog determinism, compatibility-token normalization, and parser-drift rejection already present on this branch.

## Fixer Verification Refresh

- Reverified the reviewer-fix branch tip in this lane worktree on `2026-04-17`.
- Confirmed the required fix packet remains aligned with the current branch tip after a full local gate rerun.
- Did not reproduce any failing gate output on the current branch tip; the reviewer-required fix in this pass is the refreshed passing evidence below.

## Re-Review Gate Evidence

- Review status addressed: reviewer-required fix `1. Resolve failing gate output and include passing results.`
- Re-review date: `2026-04-17`
- Passing gate rerun recorded for the current branch tip before this metadata-only commit:
  - `make scope-check`: `PASS`
  - `./quality-format.sh --check`: `PASS`
  - `./quality-lint.sh`: `PASS`
  - `./quality-test.sh`: `PASS` (`198` tests, `OK`)
  - `./typecheck-test.sh`: `PASS` (`python3 -m compileall -q src`)
  - `make ci`: `PASS`

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Canonical Demo-Path Step Advanced

- Primary step advanced: `open project/document`.
- Why this step: `feat-commands` owns the CLI operator surface that starts the current MVP loop, so deterministic canonical command ordering and compatibility-token normalization directly harden the first operator action in the canonical demo path: opening a project or document through the stable CLI entry contract.
- Concrete contract improvement:
  - `command_cli_contract()` now fails fast if the parser surface drifts from `command_names()`.
  - Canonical command ordering is returned directly from the catalog instead of being rebuilt from lookup order.
  - Demo compatibility variants normalize onto the trusted canonical command tokens instead of creating alternate entry paths.
- Scope-tightening note: this handoff claims existing MVP-loop command-contract hardening only. It does not claim new workflow behavior, new command entrypoints, new CLI UX, persistence behavior, or broader audit features.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so canonical CLI names must match `command_names()` and drift raises `ValueError`.
- Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
- Tightened demo workflow preferred command resolution and normalized demo compatibility variants in `src/qual/commands/catalog.py` so the command surface stays deterministic at the current branch tip.
- Added and retained focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection at the command-catalog boundary.
- Refreshed the handoff packet and thread pointer so re-review evaluates the true branch-tip command-surface slice with the required AGENTS structure.

## Kickoff Budget / Limits Compliance

- High-risk handoff stayed within the `4`-task cap, `30m` time budget, and the size limits for this packet refresh.
- Implementation scope remains narrow: lane-owned command files plus one approved shared test path already called out in the reviewer packet.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`; no new shared or integrator-locked implementation paths were added in this fixer refresh.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Rebuilt the handoff packet into the explicit high-risk `AGENTS.md` structure with kickoff, budget, stop-trigger, checkpoint, and handoff sections.
2. Added the concrete Milestone 3 demo-path mapping: this work strengthens `open project/document` by keeping the CLI entry contract deterministic and parser-ready.
3. Tightened roadmap and product-vision mapping so the packet claims only CLI compatibility and canonical engine contract hardening supported by the current diff.
4. Re-ran the required local gates and recorded the outcomes for this docs-only reviewer-fix refresh.

### Files Changed

- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`198` tests, `OK`)
- `./typecheck-test.sh`: `PASS` (`python3 -m compileall -q src`)
- `make ci`: `PASS`

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: none beyond normal merge sequencing for a narrow command-catalog slice.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands, specifically at the `open project/document` entry step of the engine-first MVP demo path.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the `open project/document` entry step.

### Vision capability affected

- Canonical engine contract - the CLI compatibility surface for `open project/document` stays stable and smoke-testable while Textual remains disabled.

### Routing/provider impact note

- None. This change affects local command-contract validation and command-catalog test coverage only.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail: owned implementation path is `src/qual/commands/catalog.py`; the only non-owned implementation path is the approved shared test `tests/unit/test_commands_catalog.py`.
