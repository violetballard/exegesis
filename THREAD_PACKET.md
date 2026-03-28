# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit:
  - `8852290adbbe735ced45c28b8ee43398d1af9b5c`

## Scope goal
- Harden command catalog and diff_preview output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected diff_preview fingerprint semantics so SHA-256 is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Kept the lane limited to `src/qual/commands/**` plus the approved shared command-contract tests.
- Regenerated the feature handoff packet from the real `main...HEAD` branch delta so the review packet matches the submitted branch state.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta is 9 files changed and remains within the lane size limits.
- The change stays centered on the command-contract lane and its approved shared regression coverage.

## Tasks completed (numbered)
1. Restored the feature packet to the command-contract scope instead of the stale docs-only handoff correction.
2. Reconfirmed the diff_preview fingerprint and label contract details that the branch now guarantees.
3. Kept the shared command-contract test coverage explicitly approved for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
4. Regenerated the handoff inventory so the packet matches the branch delta actually being submitted.

## Files changed
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
- `THREAD_PACKET.md`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: keep command-surface projections deterministic and make diff_preview fingerprints derive from the emitted payload.
- Milestone 2 - Test Hardening: add focused command-contract coverage for JSON, no-diff, custom-label, and fingerprint paths.
- Milestone 3 - Product Readiness: lock CLI-first command output contracts for operator use.

### Vision capability affected
- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint verifies the exact diff payload returned by the command.
- Capability 4 - Operator-first control surface: the command lane keeps a stable CLI-first surface with deterministic JSON and text output.

### Routing/provider impact note
- None. This change only affects local command output formatting, verification metadata, and focused contract coverage; no policy or routing files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
