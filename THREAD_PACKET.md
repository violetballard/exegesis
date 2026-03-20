# Feature → Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed implementation head: `3378e905fab4653d38070b8e272ce4e4c6d22908`
- Packet note: this follow-up commit adds the missing handoff packet only; the verified behavior change remains the reviewed implementation head above.

## Scope goal
- Harden `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` fingerprint semantics so SHA-256 is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Repaired lane scope checking so the approved shared-test exception for `tests/unit/test_diff_preview.py` is honored during lane verification.

## Kickoff budget/limits compliance
- Stayed within the default lane budget; the reviewed implementation delta is 3 files and 91 insertions / 1 deletion. One shared test file was added under an approved exception, and `scripts/scope-check.sh` was updated so the documented shared-test exception path works for this lane.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_diff_preview.py` to add focused contract coverage required by review.

## Tasks completed (numbered)
1. Corrected diff fingerprinting to hash the emitted diff payload after labels, header suppression, truncation, and summary-only handling so the reported SHA-256 verifies the artifact users receive.
2. Added focused unit coverage for JSON command output, no-diff JSON shape, labeled diff output, and fingerprint correctness across emitted contract paths.
3. Fixed `scripts/scope-check.sh` so `codex/feat-commands` can use the documented approved shared-test path for `tests/unit/test_diff_preview.py`, allowing `make scope-check` and `make ci` to represent the reviewed branch truthfully.
4. Regenerated the feature handoff packet so the submitted branch state has concrete scope, file, roadmap, vision, and gate evidence instead of the stale seed metadata.

## Files changed for reviewed implementation head
- `scripts/scope-check.sh`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Metadata file added in this follow-up
- `THREAD_PACKET.md`

## Commands run and outcomes
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
- Note: The lane now uses an explicit approved shared-test exception for `tests/unit/test_diff_preview.py`; no routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden the CLI diff-preview command path so emitted output stays deterministic under labels, truncation, and summary-only controls.
- Milestone 2 - Test Hardening: add focused unit coverage for the newly expanded diff-preview contract surface and no-diff JSON cases identified during review.
- Milestone 3 - Product Readiness: keep the user-facing diff preview contract explicit and verifiable by matching fingerprint metadata to the exact emitted artifact.

### Vision capability affected
- Capability 3 - Auditable generation.
- Capability 4 - Operator-first control surface.

### Routing/provider impact note
- None. This change only affects local diff-preview output formatting, verification metadata, and lane scope-check handling for the approved shared test.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
