# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: review the real branch-tip `feat-commands` command-surface implementation so the CLI-first MVP loop keeps a deterministic, smoke-testable command contract while Textual remains disabled.
- Risk reason: this lane includes the approved shared tests `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, so the handoff stays on the high-risk template even though implementation remains command-surface-only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Retarget the packet traceability to the actual current branch tip instead of the stale `f8d860e` slice.
2. State the exact canonical demo-path step this command-surface work advances.
3. Update scope and file lists so they match the real reviewed implementation range now in scope.
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

- Plan complete: reviewer-required fixes are packet traceability and demo-path alignment; no new implementation defect was identified in the packet.
- First green tests: satisfied by the full gate rerun recorded below.
- Before risky/shared file edit: approved shared-test exceptions remain limited to `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
- Ready for handoff: satisfied by this refreshed packet plus the full gate rerun recorded below.

## Packet Traceability Note

- This re-review packet is anchored to current branch tip `9ee9189503c7d173869fe55da958893194cc2c93` immediately before this metadata refresh commit.
- The latest non-metadata command-surface implementation tip in scope remains `423adf3c0b23ac152844bbe3b74577cd3afb318b`.
- The earlier commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` remains part of the reviewed history, but it is no longer treated as the sole implementation slice.
- Code changes after `f8d860e` are in scope for this re-review. The current reviewed implementation range includes:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Metadata-only handoff files for this packet refresh only:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. Retargeted the packet to the real pre-refresh implementation tip instead of claiming later code commits were metadata-only.
2. Updated the scope and in-scope file list so the handoff matches the reviewed command implementation present at `423adf3c0b23ac152844bbe3b74577cd3afb318b` and the current branch-tip metadata state at `9ee9189503c7d173869fe55da958893194cc2c93`.
3. Added the explicit `AGENTS.md` demo-path mapping by naming the exact canonical step this work makes more real and why it removes a concrete blocker there.
4. Re-ran the required gate suite from current branch tip `9ee9189503c7d173869fe55da958893194cc2c93` and recorded fresh passing evidence for re-review on `2026-04-17`.

## Fixer Verification Refresh

- Re-ran the full required gate suite on `2026-04-17` against pre-commit branch tip `9ee9189503c7d173869fe55da958893194cc2c93`.
- This metadata-only refresh records that fresh verification pass so the handoff packet matches the latest fixer run.

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
- Why this step: `feat-commands` owns the CLI operator surface that starts the current MVP loop, and the reviewed branch-tip command work keeps those entrypoints deterministic, canonical, and smoke-testable before the operator can reliably start `open project/document`.
- Concrete blocker removed:
  - parser-facing command tokens and canonical command names remain aligned with the catalog instead of drifting silently;
  - demo-path compatibility verbs stay routed through the canonical command surface rather than ad hoc aliases;
  - diff-preview smoke behavior remains covered so patch-review commands in the same operator surface stay stable.
- Scope-tightening note: this handoff claims branch-tip command-surface hardening only. It does not claim new engine workflow behavior, persistence features, routing/provider changes, or any Textual UI activation.

## Scope Completed

- Hardened the command catalog and CLI contract so canonical command ordering, parser-surface lookup, routed surface tokens, and demo compatibility verbs stay deterministic at the branch tip.
- Kept command exports and canonical wrappers aligned with the command catalog so the compatibility surface is migration-safe for the CLI-first MVP loop.
- Preserved diff-preview command stability within the same operator surface, including focused coverage for bounded diff-preview behavior.
- Retained focused regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` so the command surface remains smoke-testable at the current branch tip.
- Refreshed the handoff packet and thread pointer so re-review evaluates the true branch-tip scope with truthful traceability and explicit demo-path mapping.

## Kickoff Budget / Limits Compliance

- High-risk handoff stayed within the `4`-task cap, `30m` time budget, and the lane size limits for this fixer refresh.
- The refreshed packet now accurately reports the current branch-tip reviewed file set instead of the stale single-slice description.

## Approved Exception Note

- Approved shared-test exceptions for:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- No integrator-locked implementation files were edited in this fixer refresh.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Retargeted the handoff packet traceability to current branch tip `9ee9189503c7d173869fe55da958893194cc2c93` while preserving implementation scope at `423adf3c0b23ac152844bbe3b74577cd3afb318b`.
2. Added the explicit canonical demo-path mapping: this branch-tip command-surface work strengthens `open project/document`.
3. Updated `Scope completed`, `Files changed`, and ownership notes so they match the real command implementation now in scope for re-review.
4. Re-ran the required local gates on the current branch tip and recorded outcomes for this fixer pass.

### Files Changed

- Reviewed implementation files:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Metadata-only handoff files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`200` tests, `OK`)
- `./typecheck-test.sh`: `PASS` (`python3 -m compileall -q src`)
- `make ci`: `PASS`
- Verification date: `2026-04-17`
- Verification anchor: pre-commit branch tip `9ee9189503c7d173869fe55da958893194cc2c93`

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: normal merge sequencing only for a narrow command-surface lane.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands, specifically at the `open project/document` entry step of the engine-first MVP path.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the `open project/document` operator entry contract.

### Vision capability affected

- Canonical engine contract - the CLI compatibility surface remains stable, deterministic, and smoke-testable while Textual stays disabled.
- Auditable state and workflow - command-surface drift now fails loudly at the catalog boundary instead of silently changing the operator contract.

### Routing/provider impact note

- None. This branch-tip scope affects local command-contract validation, compatibility wrappers, diff-preview stability, and focused command tests only.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation paths stay inside `src/qual/commands/**`
  - approved shared test paths are `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`
