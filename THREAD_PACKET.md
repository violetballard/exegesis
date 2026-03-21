# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed commit: `9fb6bf4ea97d18219a2e6a5b465897c7d0554d0d`
- Branch head note: the current branch head is packet-maintenance only; review the code-changing commit above for the actual `diff_preview` delta.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required focused regression coverage so text and JSON responses stay deterministic, auditable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Preserved the lane-owned `diff_preview` contract hardening work in the reviewed code commit `src/qual/commands/diff_preview.py`, including labeled output, structured JSON payloads, stable no-diff responses, diff statistics, and fingerprint gating via `QUAL_DIFF_INCLUDE_FINGERPRINT`.
- Kept focused regression coverage in `tests/unit/test_diff_preview.py` for the reviewed `diff_preview` JSON and fingerprint contracts: JSON fingerprint-disabled output, JSON fingerprint-enabled output, labeled JSON output, stable no-diff JSON payloads, summary-only fingerprint behavior, and labeled/truncated text fingerprint behavior.
- Reissued the handoff packet against the actual code-changing commit `9fb6bf4ea97d18219a2e6a5b465897c7d0554d0d` so the scope summary, ownership note, roadmap mapping, changed-file list, and command outcomes match the reviewed delta instead of the packet-only head.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta contains one lane-owned command file, one regression test file, and this packet.

## Tasks completed (numbered)
1. Preserved the lane-owned `src/qual/commands/diff_preview.py` contract hardening work so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Kept the focused regression tests in `tests/unit/test_diff_preview.py` for the reviewed `diff_preview` JSON and fingerprint contracts.
3. Reissued the feature handoff packet so every field matches the reviewed branch state instead of the packet-maintenance head.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-21`
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
- Milestone 2 - Test Hardening: preserve the focused regression coverage in `tests/unit/test_diff_preview.py` for the JSON fingerprint-disabled payload shape, JSON fingerprint-enabled behavior, no-diff JSON shape, summary-only fingerprint behavior, and truncated text fingerprint behavior.
- Milestone 3 - Product Readiness: lock the user-facing `diff_preview` fingerprint and structured output contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first and JSON contract by covering the reviewer-requested output cases with focused regression tests.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting plus the reviewer-required regression test; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
