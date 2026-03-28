# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `2afa0f7f2f23c2d73773cc9c5a2fc0007ba19be3`

## Scope goal
- Restore the `feat-commands` scope policy so the approved shared `tests/unit/test_diff_preview.py` regression is allowed through the gate.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_diff_preview.py`
- Shared policy support:
  - `scripts/scope-check.sh`

## Scope completed
- Restored the scope-check policy allowance for the approved shared diff-preview regression so the branch gates accept the reviewed shared test.
- Regenerated the handoff packet and lane metadata so the review evidence matches the actual submitted scope.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta changes 5 files, centered on the scope-check policy allowance and the approved shared diff-preview regression for the `feat-commands` lane.
- The change stays centered on the scope gate needed to verify the reviewed regression and keep the handoff metadata truthful.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_diff_preview.py`; matching scope-check policy allowance restored in `scripts/scope-check.sh`.

## Tasks completed (numbered)
1. Restored the scope-check policy allowance for the approved shared `tests/unit/test_diff_preview.py` regression.
2. Regenerated the handoff packet and lane metadata so the review evidence matches the actual submitted scope.

## Files changed
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 3 - Product Readiness (Planned): keep lane scope checks aligned with the approved shared regression so the `feat-commands` review gate can pass without widening the command surface.

### Vision capability affected
- 4. Operator-first control surface - CLI review gates stay aligned with the approved `feat-commands` scope so the lane can ship the reviewed regression without expanding the contract surface.

### Routing/provider impact note
- None. This change only affects local scope-check policy for the approved shared test; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
