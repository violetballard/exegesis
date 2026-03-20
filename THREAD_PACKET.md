# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed commit: `1c89542b7b9bcee6f00d94ac4a24c3026755a8ff`
- Branch head note: this packet documents the actual reviewed delta. That delta is a guardrail-only revert in `scripts/scope-check.sh`.

## Scope goal
- Revert the shared policy change in `scripts/scope-check.sh` and keep the handoff metadata aligned with that policy-only branch state. No product behavior changed.

## Lane/owned paths
- Shared policy file: `scripts/scope-check.sh`

## Scope completed
- Rewrote the handoff packet so it matches the actual reviewed commit `1c89542b7b9bcee6f00d94ac4a24c3026755a8ff`.
- Removed the stale `diff_preview` claims from the handoff so the packet no longer mentions `src/qual/commands/diff_preview.py` or `tests/unit/test_diff_preview.py`.
- Kept the reviewed delta limited to a guardrail-only policy revert in `scripts/scope-check.sh`; no product behavior changed.

## Tasks completed (numbered)
1. Rewrote the handoff packet to match the actual reviewed commit `1c89542b7b9bcee6f00d94ac4a24c3026755a8ff`.
2. Removed claims that `src/qual/commands/diff_preview.py` and `tests/unit/test_diff_preview.py` changed in this commit.
3. Updated scope, files changed, and required handoff fields so they all describe the same policy-only branch state.
4. Set roadmap and vision impact to `none` because the reviewed change only reverts shared policy enforcement.

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
- Risk: `low`
- Blockers: none
- Note: this is a guardrail-only revert; no routing/provider or product behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- none

### Vision capability affected
- none

### Routing/provider impact note
- None. This change only reverts `scripts/scope-check.sh`.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approval rationale: the reviewed change is a narrow shared-policy revert in `scripts/scope-check.sh` and does not touch runtime/product code.
