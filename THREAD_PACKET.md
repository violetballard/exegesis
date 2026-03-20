# Feature → Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Branch head note: this tracked packet is part of the submitted branch head, so the final exact HEAD SHA is reported in the handoff response that accompanies this packet to avoid self-referential SHA drift inside the commit itself.

## Scope goal
- Harden `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` fingerprint semantics so SHA-256 is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused command-contract tests for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness.
- Repaired lane scope checking so the approved shared-test exception for `tests/unit/test_diff_preview.py` is honored during lane verification.
- Regenerated this handoff packet from the real `main...codex/feat-commands` delta so review maps to the branch state actually being submitted.

## Kickoff budget/limits compliance
- Stayed within the default lane budget; the submitted branch delta is 4 files changed and remains well within the lane size limits. One shared test file was added under an approved exception, and `scripts/scope-check.sh` was updated so the documented shared-test exception path works for this lane.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_diff_preview.py` to add focused contract coverage required by review.

## Tasks completed (numbered)
1. Corrected diff fingerprinting to hash the emitted diff payload after labels, header suppression, truncation, and summary-only handling so the reported SHA-256 verifies the artifact users receive.
2. Added focused unit coverage for JSON command output, no-diff JSON shape, labeled diff output, and fingerprint correctness across emitted contract paths.
3. Fixed `scripts/scope-check.sh` so `codex/feat-commands` can use the documented approved shared-test path for `tests/unit/test_diff_preview.py`, allowing `make scope-check` and `make ci` to represent the reviewed branch truthfully.
4. Regenerated the feature handoff packet so the submitted branch state has concrete scope, file, roadmap, vision, and gate evidence instead of stale or generic metadata.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

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
- Milestone 1 - Bootstrap Flow Stabilization: harden the `diff_preview` command contract so emitted CLI/JSON output stays deterministic under labels, truncation, and summary-only controls.
- Milestone 2 - Test Hardening: add focused unit coverage for JSON output, no-diff JSON shape, custom labels, and fingerprint verification of emitted diff artifacts.
- Milestone 3 - Product Readiness: keep the user-facing diff preview contract explicit and auditable by matching fingerprint metadata to the exact emitted artifact.

### Vision capability affected
- Capability 3 - Auditable generation: the advertised fingerprint now verifies the exact diff payload emitted to operators and automation.
- Capability 4 - Operator-first control surface: `diff_preview` remains a CLI-first command surface with a stable JSON fallback contract for downstream consumers.

### Routing/provider impact note
- None. This change only affects local diff-preview output formatting, verification metadata, and lane scope-check handling for the approved shared test.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
