# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed branch tip: current `codex/feat-commands` head
- Branch head note: this packet is regenerated from the actual `main...codex/feat-commands` diff for the submitted branch tip.

## Scope goal
- Harden the `diff_preview` command contract so labeled, header-suppressed, truncated, summary-only, and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` fingerprint semantics so SHA-256 is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Kept the submitted branch limited to the lane-owned command surface plus focused regression coverage in `tests/unit/test_diff_preview.py`.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The reviewed branch delta is 6 files changed and remains within the lane size limits.
- Submitted files:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD_PACKET.md`

## Tasks completed (numbered)
1. Corrected `diff_preview` fingerprinting to hash the emitted payload after labels, header suppression, truncation, and summary-only handling.
2. Added focused unit coverage for JSON command output, no-diff JSON shape, labeled diff output, and fingerprint correctness across emitted contract paths.
3. Regenerated the feature handoff packet so the file list, scope note, and roadmap/vision mapping match the final branch diff.
4. Removed the false shared-file exception so the ownership note matches `THREAD_OWNERSHIP.md`.

## Files changed for reviewed branch delta
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`
- `THREAD_PACKET.md`

## Commands run and outcomes
- Validation date: `2026-03-22`
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make scope-check`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- Note: no routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command surface so CLI responses stay deterministic and verifiable.
- Milestone 2 - Test Hardening: add focused contract coverage for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.

### Vision capability affected
- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint verifies the exact diff payload returned by the command.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first surface with a concrete JSON contract that matches the submitted behavior.

### Routing/provider impact note
- None. This change affects local command metadata and `diff_preview` output formatting only; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
