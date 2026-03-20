# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `ab22bca5e2d7aa9cb56fbbf52e7324d2c56292d6`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression coverage so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Preserved the lane-owned `diff_preview` contract hardening work in `src/qual/commands/diff_preview.py`, including JSON output and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Kept the focused shared regression coverage in `tests/unit/test_diff_preview.py` for the JSON fingerprint-disabled payload shape and the fingerprint-enabled object contract present on this branch.
- Recorded the reviewer-required shared-test approval basis in `THREAD_OWNERSHIP.md` and tightened `scripts/scope-check.sh` so the approved shared test remains deliberate behind `SCOPE_ALLOW_SHARED=1`.
- Regenerated this handoff packet so the submitted branch description matches the current tracked delta and reviewer-required fixes.

## Kickoff budget/limits compliance
- Stayed within the high-risk budget. The submitted branch delta contains one lane-owned command file, one reviewer-required shared regression test, two approval-record files, and this packet.

## Tasks completed (numbered)
1. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract hardening work so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Kept the focused shared regression tests in `tests/unit/test_diff_preview.py` for the JSON disabled-fingerprint payload shape and the enabled fingerprint object contract.
3. Recorded the reviewer-required shared-test approval in `THREAD_OWNERSHIP.md` and the matching `SCOPE_ALLOW_SHARED=1` enforcement in `scripts/scope-check.sh` so the branch has a durable approval basis.
4. Regenerated the feature handoff packet so every field matches the submitted branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `THREAD_OWNERSHIP.md`
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
- Note: No routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command behavior so JSON and text honor the same fingerprint gate.
- Milestone 2 - Test Hardening: preserve the focused JSON fingerprint regression cases in `tests/unit/test_diff_preview.py` for fingerprint-disabled and fingerprint-enabled output.
- Milestone 3 - Product Readiness: lock the user-facing `diff_preview` fingerprint contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first/JSON contract by making the disabled fingerprint shape explicit and covering it with the reviewer-required shared regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting plus a reviewer-required shared regression test; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included only to satisfy the reviewer-required regression coverage for the submitted `diff_preview` contract change. The approval basis is tracked in `THREAD_OWNERSHIP.md` for `codex/feat-commands*`, and `scripts/scope-check.sh` honors that shared-test exception only when `SCOPE_ALLOW_SHARED=1` is supplied.
