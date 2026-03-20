# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `e00623f0be7934383d64df46fdaec99d9f92f13c`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON and text both flow through the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate, returning `fingerprint: null` when disabled and the structured fingerprint object when enabled.
- Added focused regression coverage in `tests/unit/test_diff_preview.py` for both the JSON disabled-fingerprint payload shape and the enabled fingerprint object contract.
- Restored the documented `feat-commands` shared-test allowance in `scripts/scope-check.sh` so the reviewer-required regression test remains part of the submitted delta without breaking plain ownership gates.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch changes one lane-owned command file, one reviewer-required shared regression test, one documented shared-test approval entry, and this packet.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same fingerprint-emission helper as text output and returns `fingerprint: null` when disabled.
2. Added focused regression tests in `tests/unit/test_diff_preview.py` for the JSON disabled-fingerprint payload shape and the enabled fingerprint object contract.
3. Restored the `feat-commands` approved shared-test entry in `scripts/scope-check.sh` so the reviewer-required regression test passes the branch ownership gates.
4. Regenerated the feature handoff packet so the submitted branch delta, approved exception note, and gate outcomes match the corrected branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: `scripts/scope-check.sh` records the reviewer-required `feat-commands` shared-test allowance, so the submitted branch passes plain ownership gates while still restricting other shared edits. The final submitted HEAD SHA is reported in the accompanying handoff response.
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
- Milestone 1 - Bootstrap Flow Stabilization: add the missing targeted `diff_preview` JSON contract cases identified during review.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first/JSON contract by making the disabled fingerprint shape explicit and covered by focused regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting plus the reviewer-required shared regression test and approved scope-check allowance; no routing or provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included to satisfy the reviewer-required regression coverage for the submitted `diff_preview` contract change, and `scripts/scope-check.sh` records that approved exception for `feat-commands`.
