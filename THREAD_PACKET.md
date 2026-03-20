# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `e8ddc8970d46bcc2789b045fef68ebf5d6138f8f`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression coverage so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Preserved the lane-owned `diff_preview` contract hardening work in `src/qual/commands/diff_preview.py`, including labeled output, JSON payloads, no-diff responses, diff statistics, and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Restored focused regression coverage in `tests/unit/test_diff_preview.py` for the JSON fingerprint-disabled payload shape, labeled JSON output, no-diff JSON shape, summary-only fingerprint behavior, truncated text fingerprint behavior, and the JSON fingerprint-enabled object contract.
- Added the explicit `feat-commands` shared-test approval entries in `THREAD_OWNERSHIP.md` and `scripts/scope-check.sh` so the reviewer-required regression test is part of the submitted branch and passes the required scope gates.
- Regenerated this handoff packet from the actual `codex/integrator..HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta contains one lane-owned command file, one reviewer-required shared regression test, two approval-record files, and this packet.

## Tasks completed (numbered)
1. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract hardening work so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Restored the focused shared regression tests in `tests/unit/test_diff_preview.py` for the reviewed `diff_preview` JSON and fingerprint contracts.
3. Added the `feat-commands` shared-test approval entries in `THREAD_OWNERSHIP.md` and `scripts/scope-check.sh` so the shared regression file is explicitly approved for this branch.
4. Regenerated the feature handoff packet so every field matches the submitted branch state.

## Files changed for submitted branch delta
- `THREAD_OWNERSHIP.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

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
- Note: no routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command behavior so JSON and text honor the same fingerprint gate.
- Milestone 2 - Test Hardening: preserve the focused JSON fingerprint regression cases in `tests/unit/test_diff_preview.py` for fingerprint-disabled and fingerprint-enabled output.
- Milestone 3 - Product Readiness: lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract by covering the reviewer-requested output cases with focused regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting, the reviewer-required shared regression test, and the corresponding scope-check approval entries; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included only to satisfy the reviewer-required regression coverage for the submitted `diff_preview` contract change, and `THREAD_OWNERSHIP.md` plus `scripts/scope-check.sh` record the approved `feat-commands` shared-test exception.
