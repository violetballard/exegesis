# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `5327002441c370f824590a3f9d74c9c0782dbc4a`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract inside the lane-owned command module so labeled, text, and JSON responses stay deterministic and suitable for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Removed the out-of-lane `scripts/scope-check.sh` policy change from this lane.
- Removed the out-of-lane shared test delta so the submitted branch no longer depends on an unapproved shared-file exception.
- Kept the lane-owned `diff_preview` contract hardening work in `src/qual/commands/diff_preview.py`, including label handling, JSON output, no-diff JSON responses, diff statistics, and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta after cleanup.

## Kickoff budget/limits compliance
- Stayed within the default lane budget and within lane-owned paths for the submitted branch delta.

## Tasks completed (numbered)
1. Removed the `scripts/scope-check.sh` branch change so this lane no longer edits repository enforcement policy.
2. Removed the `tests/unit/test_diff_preview.py` branch change so this lane no longer depends on an unapproved shared test path.
3. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract hardening work.
4. Regenerated the feature handoff packet so the submitted branch delta and gate outcomes match the corrected branch state.

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
- Note: No routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden `diff_preview` command behavior inside the `feat-commands` lane-owned module.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` output contract for text and JSON consumers.

### Vision capability affected
- Capability 3 - Auditable generation: `diff_preview` exposes explicit fingerprint and summary metadata in the emitted command contract instead of leaving those details implicit.
- Capability 4 - Operator-first control surface: the command provides deterministic structured output that remains suitable for CLI-first operation.

### Routing/provider impact note
- None. This change is limited to local `diff_preview` command formatting and output-contract behavior.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
- Shared-file exception note: none
