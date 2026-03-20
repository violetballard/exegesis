# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this packet refresh: `5effcd1ccdb4a7a72a65ac3b356a3a5416fc6f1d`
- Branch head note: this tracked packet is part of the fix commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Narrow the submitted lane back to the `diff_preview` command contract work and remove the off-scope policy/tooling change identified in review.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Kept the `diff_preview` command contract updates that align text and JSON fingerprint behavior behind `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Removed the lane-local `scripts/scope-check.sh` policy change so this branch no longer carries enforcement logic inside `feat-commands`.
- Regenerated this handoff packet from the corrected `codex/integrator...HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta is now `2` files total: one lane-owned command file and this handoff packet.

## Tasks completed (numbered)
1. Preserved the `src/qual/commands/diff_preview.py` contract changes so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Reverted `scripts/scope-check.sh` to the merge-base behavior so `feat-commands` no longer carries a tooling/policy exception.
3. Regenerated the feature handoff packet so the submitted branch delta, scope statement, and ownership notes match the corrected branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`

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
- Note: no routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: tighten the `diff_preview` command contract so text and JSON output stay deterministic under the same fingerprint gate.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract for operator-visible output.

### Routing/provider impact note
- None. This change affects only local `diff_preview` output formatting and the handoff packet; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
- Shared-file exception note: none carried in this lane. Any shared-test approval entry must land as a separate approved tooling/policy change outside `feat-commands`.
