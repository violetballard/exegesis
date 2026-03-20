# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `f54b7396fd85c51e7c97c0e07c460bd6d9421d4a`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and retain the reviewer-required shared regression coverage so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON and text both flow through the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate, returning `fingerprint: null` when disabled and the structured fingerprint object when enabled.
- Kept focused regression coverage in `tests/unit/test_diff_preview.py` for both the JSON disabled-fingerprint payload shape and the enabled fingerprint object contract.
- Removed the out-of-lane `scripts/scope-check.sh` policy change from the submitted branch so no policy files are changed on this lane.
- Restored this handoff packet to the submitted branch and regenerated it from the corrected `codex/integrator...HEAD` delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta is 3 files total: one lane-owned command file, one reviewer-required shared regression test, and this packet.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Restored the focused shared regression tests in `tests/unit/test_diff_preview.py` for the JSON disabled-fingerprint payload shape and the enabled fingerprint object contract.
3. Removed the out-of-lane `scripts/scope-check.sh` policy change from the submitted branch instead of carrying it forward in `feat-commands`.
4. Restored and regenerated the feature handoff packet so the submitted branch delta, scope statement, ownership note, and gate outcomes match the corrected branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: the files listed above are the full corrected `codex/integrator...HEAD` branch delta. This lane contains only the command-contract change, the reviewer-required shared regression test, and this packet; no policy files are changed.
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
- Milestone 1 - Bootstrap Flow Stabilization: add the missing targeted `diff_preview` JSON contract case identified during review.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first/JSON contract by making the disabled fingerprint shape explicit and covered by the reviewer-required shared regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting plus the reviewer-required shared regression test; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved exception note: `tests/unit/test_diff_preview.py` is included only to satisfy the reviewer-required regression coverage for the submitted `diff_preview` contract change. No policy files are changed on this branch.
