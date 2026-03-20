# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `a45f7ac2b308b1ba31ccffb12c23b0fc4d368a33`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression coverage so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Preserved the lane-owned `diff_preview` contract hardening work in `src/qual/commands/diff_preview.py`, including labeled output, JSON payloads, no-diff responses, diff statistics, and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Kept the reviewer-required shared regression coverage in `tests/unit/test_diff_preview.py` as the only shared-file exception for the expanded `diff_preview` contract.
- Left lane policy enforcement unchanged and documented the shared-file exception here rather than self-authorized in `THREAD_OWNERSHIP.md` or `scripts/scope-check.sh`.
- Regenerated this handoff packet from the actual `codex/feat-commands` branch delta so the scope summary, ownership note, roadmap mapping, changed-file list, and command outcomes match the submitted branch.

## Kickoff budget/limits compliance
- Stayed within the high-risk budget. The submitted branch delta contains one lane-owned command file, one reviewer-required shared regression test, and this packet.

## Tasks completed (numbered)
1. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract hardening work so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Restored the focused shared regression tests in `tests/unit/test_diff_preview.py` for the reviewed `diff_preview` JSON and fingerprint contracts.
3. Kept the shared-test approval external to lane policy enforcement and captured the exception as an explicit note in this packet instead.
4. Regenerated the feature handoff packet so every field matches the submitted branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

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
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command behavior so JSON and text honor the same fingerprint gate.
- Milestone 2 - Test Hardening: preserve the focused regression coverage in `tests/unit/test_diff_preview.py` for the JSON fingerprint-disabled payload shape, JSON fingerprint-enabled behavior, no-diff JSON shape, summary-only fingerprint behavior, and truncated text fingerprint behavior.
- Milestone 3 - Product Readiness: lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract by covering the reviewer-requested output cases with focused regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting plus the reviewer-required shared regression test; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is the only shared-file exception in this submission.
