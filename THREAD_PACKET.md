# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `0069e7f9fde81c13c9853f929ea1b1f352205d84`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Keep the branch inside `feat-commands` ownership by dropping the unapproved shared-test path while preserving the lane-owned `diff_preview` command-contract hardening.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Removed the out-of-lane `scripts/scope-check.sh` change from the submitted branch so the lane delta no longer carries repository policy edits.
- Removed the out-of-lane `tests/unit/test_diff_preview.py` regression delta so the submitted branch no longer needs a shared-file exception.
- Preserved the lane-owned `diff_preview` contract hardening work in `src/qual/commands/diff_preview.py`, including labeled output, JSON payloads, stable no-diff responses, diff statistics, and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta after the reviewer-required cleanup.

## Kickoff budget/limits compliance
- Stayed within the default lane budget and within lane-owned paths for the submitted branch delta. The submitted branch delta contains one lane-owned command file and this packet.

## Tasks completed (numbered)
1. Removed the out-of-scope `scripts/scope-check.sh` branch delta.
2. Removed the out-of-scope `tests/unit/test_diff_preview.py` branch delta.
3. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract hardening work so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
4. Regenerated `THREAD_PACKET.md` so the handoff fields now match the submitted `codex/integrator...HEAD` delta exactly.

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
- Note: no routing/provider behavior changed and no shared/integrator-locked files remain in the submitted delta.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command behavior so JSON and text honor the same fingerprint gate.
- Milestone 3 - Product Readiness: lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract inside the lane-owned command module.

### Routing/provider impact note
- None. This change affects only local `diff_preview` output formatting and metadata behavior; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
- Shared-file exception note: none
