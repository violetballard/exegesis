# Feature → Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `5994fd9ae6615c732ee364621e7261576395ca26`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON respects `QUAL_DIFF_INCLUDE_FINGERPRINT` the same way text output does, returning `null` fingerprint metadata when the flag is disabled.
- Added focused regression coverage for the JSON disabled-fingerprint path so the payload shape is explicit and protected against contract drift.
- Regenerated this handoff packet so it consistently records the shared test-file exception included in the submitted branch.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch includes one shared test-file exception in `tests/unit/test_diff_preview.py`, documented here to match the submitted state.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate as text output and returns `fingerprint: null` when disabled.
2. Added a focused regression test in `tests/unit/test_diff_preview.py` for JSON output with fingerprint gating disabled.
3. Regenerated the feature handoff packet so the ownership note and shared test-file exception consistently match the submitted branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: the reviewer-required shared test-file exception causes the plain ownership gate to fail until `SCOPE_ALLOW_SHARED=1` is supplied. The final submitted HEAD SHA is reported in the accompanying handoff response.
- `python -m unittest tests.unit.test_diff_preview`: PASS
- `make scope-check`: FAIL (expected ownership stop on shared file `tests/unit/test_diff_preview.py`)
- `SCOPE_ALLOW_SHARED=1 make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: FAIL (expected ownership stop on shared file `tests/unit/test_diff_preview.py`)
- `SCOPE_ALLOW_SHARED=1 make ci`: PASS

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
- None. This change only affects local diff-preview output formatting plus a shared regression test; no policy, routing, or provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included to satisfy the reviewer-required contract regression coverage for the submitted `diff_preview` behavior change.
