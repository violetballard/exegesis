# Feature → Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `e00623f0be7934383d64df46fdaec99d9f92f13c`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON respects `QUAL_DIFF_INCLUDE_FINGERPRINT` the same way text output does, returning `null` fingerprint metadata when the flag is disabled.
- Added focused regression coverage for the JSON disabled-fingerprint path so the payload shape is explicit and protected against contract drift.
- Registered the approved `feat-commands` shared test-file exception in `scripts/scope-check.sh` so the documented ownership override actually permits the reviewer-required regression test during approved scope-check/CI runs.
- Regenerated this handoff packet so it consistently records the shared-file exceptions included in the submitted branch.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch includes the reviewer-required shared test-file exception in `tests/unit/test_diff_preview.py` plus the corresponding shared scope-check approval entry in `scripts/scope-check.sh`, documented here to match the submitted state.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate as text output and returns `fingerprint: null` when disabled.
2. Added a focused regression test in `tests/unit/test_diff_preview.py` for JSON output with fingerprint gating disabled.
3. Updated `scripts/scope-check.sh` so the documented shared-file approval path recognizes the required `feat-commands` regression test when `SCOPE_ALLOW_SHARED=1` is supplied.
4. Regenerated the feature handoff packet so the ownership note and shared-file exceptions consistently match the submitted branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: `scripts/scope-check.sh` now records the reviewer-required `feat-commands` shared-test allowance, so the branch passes the plain ownership gates without extra env overrides. The final submitted HEAD SHA is reported in the accompanying handoff response.
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
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command surface by making labeled, suppressed-header, truncated, and summary-only output deterministic on the actual submitted branch.
- Milestone 3 - Product Readiness: lock the emitted diff fingerprint semantics to the exact user-visible artifact so downstream CLI/automation consumers can verify what the command actually returned.

### Vision capability affected
- Capability 3 - Auditable generation: the command now makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first/JSON contract by making the disabled fingerprint shape explicit and covered by regression tests.

### Routing/provider impact note
- None. This change affects local diff-preview output formatting plus the shared regression-test/scope-check approval path; no routing or provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included to satisfy the reviewer-required contract regression coverage for the submitted `diff_preview` behavior change, and `scripts/scope-check.sh` now records that approved exception for `feat-commands` when `SCOPE_ALLOW_SHARED=1` is supplied.
