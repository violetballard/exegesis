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
- Corrected `diff_preview` fingerprint semantics so SHA-256 is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Regenerated this handoff packet after removing the out-of-lane scope-policy change so review maps to the remaining in-scope branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget; the submitted branch delta is 3 files changed and remains well within the lane size limits. The change stays centered on the `diff_preview` command contract with one focused shared test file.

## Approved exception note
- Focused shared test coverage remains limited to `tests/unit/test_diff_preview.py` for the `diff_preview` command contract.

## Tasks completed (numbered)
1. Corrected diff fingerprinting to hash the emitted diff payload after labels, header suppression, truncation, and summary-only handling so the reported SHA-256 verifies the artifact users receive.
2. Added focused unit coverage for JSON command output, no-diff JSON shape, labeled diff output, and fingerprint correctness across emitted contract paths.
3. Regenerated the feature handoff packet so the submitted branch state has concrete scope, file, roadmap, vision, and gate evidence instead of stale or generic metadata.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: the remaining in-scope branch delta was revalidated from the working tree atop `5994fd9ae6615c732ee364621e7261576395ca26` immediately before this fix commit. The final submitted HEAD SHA is reported in the accompanying handoff response.
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
- Milestone 2 - Test Hardening: add focused unit coverage for the exact new command-output contract paths introduced on this branch, including JSON success output, JSON no-diff shape, custom labels, and fingerprint verification.
- Milestone 3 - Product Readiness: lock the emitted diff fingerprint semantics to the exact user-visible artifact so downstream CLI/automation consumers can verify what the command actually returned.

### Vision capability affected
- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint now verifies the exact diff payload returned by the command, including label application and truncation behavior.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first surface while exposing a concrete JSON contract that matches the submitted behavior change and is covered by focused tests.

### Routing/provider impact note
- None. This change only affects local diff-preview output formatting, verification metadata, and focused `diff_preview` test coverage.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
