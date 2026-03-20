# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed commit: `51279575df18d44dc112129f561f2dcb7743e70f`
- Branch head note: this packet documents the actual reviewed delta. That delta is a single shared policy-file edit in `scripts/scope-check.sh`.

## Scope goal
- Restore the approved shared-test allowance in `scripts/scope-check.sh` so `codex/feat-context-storage*` can keep its lane-approved unit coverage under scope enforcement.

## Lane/owned paths
- Shared policy file: `scripts/scope-check.sh`
- Shared edit approval: explicit lane/integrator approval is required and recorded for this policy exception.

## Scope completed
- Added the approved shared-test allowance in `scripts/scope-check.sh` for `codex/feat-context-storage*` to permit `tests/unit/test_context_storage_recovery.py`.
- Kept the reviewed branch delta limited to scope-enforcement policy only.
- Removed the stale diff-preview claims from the handoff so the packet matches the actual commit.

## Tasks completed (numbered)
1. Rewrote the handoff packet to match the actual reviewed commit `51279575df18d44dc112129f561f2dcb7743e70f`.
2. Removed claims that `src/qual/commands/diff_preview.py` and `tests/unit/test_diff_preview.py` changed in this commit.
3. Updated scope, files changed, and required handoff fields so they all describe the same policy-only branch state.
4. Reframed the roadmap/vision mapping as `none` because the reviewed change only restores a shared policy allowance.
5. Added an explicit approval rationale for the shared policy edit under `AGENTS.md` and `INTEGRATION.md`.

## Files changed for submitted branch delta
- `scripts/scope-check.sh`

## Commands run and outcomes
- Validation date: `2026-03-20`
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `medium`
- Blockers: none
- Note: this is a shared policy-file edit, but it is narrowly scoped to restoring an approved shared-test allowance and does not change product behavior, routing, or command contracts.

## Required handoff fields
### Roadmap item(s) affected
- none

### Vision capability affected
- none

### Routing/provider impact note
- None. This change only updates shared scope-enforcement policy.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approval rationale: acceptable under `AGENTS.md` and `INTEGRATION.md` because the change is a narrow, explicitly approved shared-policy exception, limited to `scripts/scope-check.sh`, and it only restores an allowed lane test path without touching runtime/product code.
