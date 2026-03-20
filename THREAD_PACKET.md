# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `f54b7396c3d4c5c57131628dc2da295887137bc2`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression test so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON and text both flow through the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate, returning `fingerprint: null` when disabled and the structured fingerprint object when enabled.
- Kept the focused shared regression coverage in `tests/unit/test_diff_preview.py` for the JSON disabled-fingerprint payload shape and enabled fingerprint behavior required by review.
- Removed the out-of-lane `scripts/scope-check.sh` policy change from this lane so the submitted branch no longer changes repository scope policy.
- Regenerated this handoff packet from the real `codex/integrator...HEAD` branch delta and the observed gate outcomes on `2026-03-20`.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta is 3 files total: one lane-owned command file, one reviewer-required shared regression test, and this packet.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Kept the focused shared regression tests in `tests/unit/test_diff_preview.py` for the JSON disabled-fingerprint payload shape and enabled fingerprint behavior.
3. Removed the out-of-lane `scripts/scope-check.sh` policy change so the submitted branch no longer alters repository ownership enforcement.
4. Regenerated the feature handoff packet so the submitted branch delta, ownership note, and gate outcomes match the corrected branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: the files listed above are the full `codex/integrator...HEAD` branch delta after removing the out-of-lane `scripts/scope-check.sh` edit from the lane.
- `python -m unittest tests.unit.test_diff_preview`: PASS
- `make scope-check`: FAIL (`tests/unit/test_diff_preview.py` is treated as out-of-lane by the default scope-check invocation)
- `SCOPE_WINDOW=full make scope-check`: PASS
- `SCOPE_ALLOW_SHARED=1 SCOPE_WINDOW=full make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: FAIL (`tests/unit/test_diff_preview.py` is treated as out-of-lane by the default scope-check invocation inside CI)
- `SCOPE_WINDOW=full make ci`: PASS
- `SCOPE_ALLOW_SHARED=1 SCOPE_WINDOW=full make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- Note: No routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: add the targeted `diff_preview` JSON fingerprint contract behavior identified during review.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first/JSON contract by making the disabled fingerprint shape explicit and covered by the reviewer-required shared regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting plus the reviewer-required shared regression test; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included only to satisfy the reviewer-required regression coverage for the submitted `diff_preview` contract change.
