# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `dcadd9adc358952808b58fefa26b68deb2f6ee42`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Narrow `diff_preview` back to behavior already covered by the existing command tests, keep the submitted branch inside lane ownership, and regenerate the handoff packet from the real delta.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Removed the branch-local `tests/unit/test_diff_preview.py` regression delta so the submitted branch no longer depends on a shared-file exception.
- Removed the untested JSON/label/fingerprint contract expansion from `src/qual/commands/diff_preview.py`, narrowing the branch back to behavior already covered by the existing command tests.
- Kept the lane-owned summary-stat refactor in `src/qual/commands/diff_preview.py`.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta after the reviewer-required cleanup.

## Kickoff budget/limits compliance
- Stayed within the default lane budget and within lane-owned paths for the submitted branch delta.

## Tasks completed (numbered)
1. Removed the out-of-scope `tests/unit/test_diff_preview.py` branch delta.
2. Narrowed `src/qual/commands/diff_preview.py` back to behavior already covered by the existing command tests.
3. Regenerated the feature handoff packet so every field matches the submitted branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- `python -m unittest tests.unit.test_diff_preview`: PASS
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
- Milestone 1 - Bootstrap Flow Stabilization: keep `diff_preview` behavior stable inside the lane-owned command module while removing unsupported contract drift from the submitted branch.

### Vision capability affected
- Capability 4 - Operator-first control surface: the command branch now preserves the existing CLI-visible behavior that is already covered by the focused command tests.

### Routing/provider impact note
- None. This change is limited to local `diff_preview` command behavior cleanup inside the lane-owned module.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
- Approved exception note: none
