# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `8414d91fbbdb0170bb731e3db7b5da66a86d60d0`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Remove the reviewer-rejected off-scope deltas from this lane and regenerate the handoff packet so it matches the submitted branch exactly.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Removed the out-of-lane `scripts/scope-check.sh` change from the submitted branch so the lane delta no longer carries repository policy edits.
- Removed the out-of-lane `tests/unit/test_diff_preview.py` regression delta so the submitted branch no longer needs a shared-file exception.
- Removed the lane-owned `src/qual/commands/diff_preview.py` contract-expansion delta so the submitted branch no longer claims command behavior that is not supported by the final branch state.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta after the reviewer-required cleanup.

## Kickoff budget/limits compliance
- Stayed within the default lane budget and within lane-owned paths for the submitted branch delta.

## Tasks completed (numbered)
1. Removed the out-of-scope `scripts/scope-check.sh` branch delta.
2. Removed the out-of-scope `tests/unit/test_diff_preview.py` branch delta.
3. Removed the unsupported `src/qual/commands/diff_preview.py` contract-expansion delta so the submitted branch no longer carries inaccurate scope claims.
4. Regenerated `THREAD_PACKET.md` so the handoff fields now match the submitted `codex/integrator...HEAD` delta exactly.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`

## Commands run and outcomes
- Validation date: `2026-03-20`
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- Note: no routing/provider behavior changed and no shared/integrator-locked files remain in the submitted delta.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: remove unsupported `diff_preview` branch drift so the lane handoff matches the actual command state submitted for review.

### Vision capability affected
- Capability 4 - Operator-first control surface: the submitted branch no longer claims command-contract behavior beyond the tested CLI-visible baseline.

### Routing/provider impact note
- None. This fix removes off-scope and unsupported branch drift; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
- Approved exception note: none
