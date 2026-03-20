# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this packet refresh: `68907770d3fccb78faeb4441dd9c0e30a42f9f09`
- Branch head note: this tracked packet is part of the follow-up fix commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression coverage aligned with the submitted branch so text and JSON responses stay deterministic, auditable, and CLI-first.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Kept the `diff_preview` command contract updates that align text and JSON fingerprint behavior behind `QUAL_DIFF_INCLUDE_FINGERPRINT`, including stable no-diff JSON responses and labeled output handling.
- Restored the focused shared regression coverage in `tests/unit/test_diff_preview.py` for JSON fingerprint-disabled output, labeled JSON fingerprint output, stable no-diff JSON payloads, truncated text fingerprint behavior, and summary-only fingerprint behavior.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta is `3` files total: one lane-owned command file, one reviewer-required shared regression test, and this handoff packet.

## Tasks completed (numbered)
1. Preserved the `src/qual/commands/diff_preview.py` contract changes so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Restored the focused shared regression tests in `tests/unit/test_diff_preview.py` for the reviewed `diff_preview` JSON and fingerprint contracts, including no-diff JSON shape, labeled output, truncated text fingerprinting, and summary-only fingerprint behavior.
3. Regenerated the feature handoff packet so the submitted branch delta, roadmap mapping, and ownership note match the corrected branch state exactly.

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
- Milestone 1 - Bootstrap Flow Stabilization: tighten the `diff_preview` command contract so text and JSON output stay deterministic under the same fingerprint gate.
- Milestone 2 - Test Hardening: restore the focused regression coverage for JSON fingerprint behavior, no-diff JSON shape, truncated text fingerprinting, and summary-only JSON fingerprint output.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract by covering the reviewer-requested output cases with focused regression tests.

### Routing/provider impact note
- None. This change affects only local `diff_preview` output formatting, the reviewer-required shared regression test, and the handoff packet; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is intentionally included as the reviewer-required shared regression test for the submitted `diff_preview` contract change.
