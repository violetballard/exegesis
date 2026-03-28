# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit:
  - `e9d91fc059132dc49db559f1afb06187a994165a`

## Scope goal
- Harden command catalog and diff_preview output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared test coverage: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`

## Scope completed
- Corrected diff preview fingerprinting so SHA-256 is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-surface coverage for catalog lookup/projection behavior and diff_preview JSON, no-diff, label, and fingerprint contract paths.
- Kept the branch scoped to the command lane plus the approved shared unit tests that verify the operator-facing contract.
- Regenerated the handoff packet and lane metadata from the real `main...HEAD` branch delta so review maps to the files actually changed in this lane.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta is 9 files changed and remains within the lane size limits.
- The change stays centered on the command-surface contract work and the truthful handoff metadata for the feat-commands lane.

## Tasks completed (numbered)
1. Corrected diff fingerprint semantics so the reported SHA-256 verifies the artifact users actually receive.
2. Added focused unit coverage for command catalog lookup/projection behavior and diff_preview JSON, no-diff, label, and fingerprint contract paths.
3. Kept the submitted branch aligned with the approved shared test exceptions for the command contract coverage.
4. Regenerated the feat-commands handoff packet so it reflects the actual branch delta instead of the stale docs-only packet sync.

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
- Milestone 1 - Bootstrap Flow Stabilization: harden the command and diff-preview behavior that feeds the CLI-first operator flow.
- Milestone 2 - Test Hardening: add focused unit coverage for the exact command-output contract paths introduced on this branch.

### Vision capability affected
- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint now verifies the exact diff payload returned by the command.
- Capability 4 - Operator-first control surface: the CLI-facing diff_preview and command catalog contracts stay stable, deterministic, and test-covered.

### Routing/provider impact note
- None. This branch does not change routing/provider files; the delta is limited to command contracts, diff_preview formatting, and lane metadata.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
