# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `e8ddc8970e94eacd6bf38ee567f9e8c0821e78d9`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression coverage so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Preserved the lane-owned `diff_preview` contract hardening in `src/qual/commands/diff_preview.py`, including labeled output, JSON payloads, no-diff responses, diff statistics, and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Restored focused regression coverage in `tests/unit/test_diff_preview.py` for the JSON fingerprint-disabled payload shape, labeled JSON output, no-diff JSON shape, summary-only fingerprint behavior, truncated text fingerprint behavior, and the JSON fingerprint-enabled object contract.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` submitted delta so the recorded scope, ownership note, roadmap mapping, and changed-file list match the branch under review.

## Kickoff budget/limits compliance
- Stayed within the high-risk budget. The submitted branch delta contains `3` files total: this handoff packet, the lane-owned command file, and the shared regression-test file.

## Tasks completed (numbered)
1. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract work so text and JSON output continue to honor the same fingerprint gate.
2. Restored the submitted branch's shared regression-test change in `tests/unit/test_diff_preview.py`, keeping focused test-hardening scope paired with the command change.
3. Regenerated the feature handoff packet so every reported field matches the actual `codex/integrator...HEAD` submitted branch delta.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- `make scope-check`: pending
- `./quality-format.sh --check`: pending
- `./quality-lint.sh`: pending
- `./quality-test.sh`: pending
- `./typecheck-test.sh`: pending
- `make ci`: pending

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- Note: no routing/provider behavior changed. The only non-owned path in the submitted delta is the reviewer-required focused shared regression test.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command behavior so JSON and text honor the same fingerprint gate.
- Milestone 2 - Test Hardening: the submitted branch includes the shared `tests/unit/test_diff_preview.py` regression-test delta, so it still maps to focused test hardening in addition to the command change.
- Milestone 3 - Product Readiness: lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract, and the submitted branch still carries the paired shared regression-test coverage in `tests/unit/test_diff_preview.py`.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting and the submitted shared regression-test delta; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file note: `tests/unit/test_diff_preview.py` is part of the submitted branch delta, so this handoff includes shared regression-test scope and cannot be represented as lane-owned-only work.
