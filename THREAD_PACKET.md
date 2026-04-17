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

- This reviewer-fix refresh is anchored to pre-commit branch tip `55740f8874ec0ba959752554fadc5463788f5f81`.
- Reviewed implementation commit in scope:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - lock `command_cli_contract()` to canonical catalog ordering and reject parser/catalog drift.
- Later packet-refresh commits are treated as metadata-only unless this handoff is regenerated again.
- Reviewer-fix scope in this refresh: keep the high-risk handoff structure explicit, preserve the concrete demo-path mapping, and narrow the claims to the command-catalog contract-hardening slice only.

## Reviewer Required Fixes Satisfied

1. Added the explicit canonical demo-path mapping for this slice: it strengthens the `open project/document` step by keeping the CLI entry contract deterministic while Textual remains disabled.
2. Tightened the scope wording so this packet describes a narrow command-catalog contract-hardening slice, not broader completion of the whole `feat-commands` lane or other command-surface work.
3. Regenerated the handoff packet with the required `AGENTS.md` plan-alignment statements and without claiming unrelated gate-failure remediation.
4. Re-ran the required gate suite on the current branch tip and recorded this fixer pass as a fresh metadata-only re-review verification.

## Fixer Verification Refresh

- Reverified the reviewer-fix branch tip in this lane worktree on `2026-04-17`.
- Confirmed the refreshed packet now satisfies the reviewer’s three required metadata fixes: explicit demo-path mapping, narrower slice wording, and regenerated handoff structure.
- Re-ran the required local gates on the current branch tip so the refreshed packet carries fresh passing evidence for re-review.
- This commit is a metadata-only verification refresh after prior packet commit `55740f8874ec0ba959752554fadc5463788f5f81`.

## Re-Review Gate Evidence

- Re-review date: `2026-04-17`
- Passing gate rerun recorded for the current branch tip before this metadata-only commit:
  - `make scope-check`: `PASS`
  - `./quality-format.sh --check`: `PASS`
  - `./quality-lint.sh`: `PASS`
  - `./quality-test.sh`: `PASS` (`198` tests, `OK`)
  - `./typecheck-test.sh`: `PASS` (`python3 -m compileall -q src`)
  - `make ci`: `PASS`
- Verification anchor for this rerun: pre-commit branch tip `55740f8874ec0ba959752554fadc5463788f5f81`.

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
- Why this step: `feat-commands` owns the CLI operator surface that starts the current MVP loop, and the reviewed command-catalog change hardens that first operator action by preventing silent parser/catalog drift before `open project/document` runs.
- Concrete contract improvement:
  - `command_cli_contract()` now fails fast if the parser surface drifts from `command_names()`.
  - Canonical command ordering is returned directly from the catalog instead of being rebuilt from lookup order.
  - Regression coverage verifies canonical-order alignment and drift rejection at the command-catalog boundary.
- Scope-tightening note: this handoff claims the reviewed `command_cli_contract()` command-catalog hardening slice only. It does not claim new workflow behavior, new command entrypoints, new CLI UX, persistence behavior, or broader audit features.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so canonical CLI names must match `command_names()` and drift raises `ValueError`.
- Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
- Added and retained focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection at the command-catalog boundary.
- Refreshed the handoff packet and thread pointer so re-review evaluates the true branch-tip command-catalog hardening slice with the required AGENTS structure.

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
