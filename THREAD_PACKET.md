# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this packet-alignment commit: `bf503a54b80e20c592029fd24e287a64b91c4473`
- Branch head note: this tracked packet is part of the submitted follow-up commit, so the final exact `HEAD` SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required shared regression coverage and scope-check exception handling aligned with the submitted branch so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON and text both flow through the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate, returning `fingerprint: null` when disabled and the structured fingerprint object when enabled.
- Kept focused regression coverage in `tests/unit/test_diff_preview.py` for the JSON fingerprint-disabled payload shape, labeled JSON output, no-diff JSON shape, summary-only fingerprint behavior, truncated text fingerprint behavior, and the JSON fingerprint-enabled object contract.
- Updated `scripts/scope-check.sh` so the reviewer-required `tests/unit/test_diff_preview.py` shared regression file is recognized as the approved `feat-commands` shared-test exception during scope enforcement.
- Regenerated this handoff packet from the corrected `codex/integrator...HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta is `4` files total: one lane-owned command file, one reviewer-required shared regression test, the scope-check policy helper that records that exception, and this packet.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Kept the focused shared regression tests in `tests/unit/test_diff_preview.py` for the reviewed `diff_preview` JSON and fingerprint contracts, including no-diff JSON shape, labeled output, truncated text fingerprinting, and summary-only fingerprint behavior.
3. Updated `scripts/scope-check.sh` so the submitted shared regression test is encoded as the approved `feat-commands` shared-test exception.
4. Regenerated the feature handoff packet so the submitted branch delta, scope statement, roadmap mapping, and ownership note match the corrected branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
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
- Milestone 1 - Bootstrap Flow Stabilization: add the targeted `diff_preview` command-contract regressions identified during review.
- Milestone 2 - Test Hardening: keep the focused regression coverage for the submitted `diff_preview` JSON, fingerprint, no-diff, truncation, and summary-only contract cases.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract by covering the reviewer-requested output cases with focused regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting, the reviewer-required shared regression test, and scope-check recognition of that approved shared-test exception; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Shared-file exception note: `tests/unit/test_diff_preview.py` is included only to satisfy the reviewer-required regression coverage for the submitted `diff_preview` contract change, and `scripts/scope-check.sh` records that approved `feat-commands` shared-test exception so `make scope-check` validates the submitted branch state accurately.
