# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit(s):
  - `3b4de0153788cfe2f35a761759d052dc2789fdf2`
  - `4f1c25fa61974359518ca05eb5c9bb3ddb927427`
  - `3378e905fab4653d38070b8e272ce4e4c6d22908`

## Scope goal
- Harden `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Approved shared-file exception
- `tests/unit/test_diff_preview.py`
- Approved for focused contract coverage needed to verify `diff_preview` JSON/text behavior and fingerprint semantics.

## Scope completed
- Hardened `diff_preview` output contracts so the SHA-256 fingerprint is derived from the exact emitted diff payload after label application, header suppression, truncation, and summary-only handling.
- Added focused unit coverage for JSON output, no-diff JSON shape, custom labels, and fingerprint correctness across the emitted contract paths.
- Regenerated the handoff packet so review points at the actual code-bearing `diff_preview` commits instead of the packet-only follow-ups.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The diff-preview code delta is 2 files changed and remains within the lane size limits.

## Tasks completed (numbered)
1. Hardened `diff_preview` fingerprint semantics so the reported digest matches the emitted artifact after labels, suppression, truncation, and summary-only handling.
2. Added focused unit tests for diff-preview JSON output, no-diff payloads, custom labels, and fingerprint correctness.
3. Removed stale shared-file exception wording so the packet matches the current `THREAD_OWNERSHIP.md` map.
4. Regenerated the handoff packet so the feature review points at the code-bearing `diff_preview` commits instead of the docs-only packet sync commits.

## Files changed for this turn
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`
- `THREAD_PACKET.md`

## Commands run and outcomes
- `make scope-check`: not run yet
- `./quality-format.sh --check`: not run yet
- `./quality-lint.sh`: not run yet
- `./quality-test.sh`: not run yet
- `./typecheck-test.sh`: not run yet
- `make ci`: not run yet

## Risks / blockers
- Risk: `LOW`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: keep the command surface deterministic for CLI-first operator flows.
- Milestone 2 - Test Hardening: add focused contract coverage for diff-preview output and fingerprint handling.
- Milestone 3 - Product Readiness: lock the emitted diff fingerprint semantics to the exact user-visible artifact.

### Vision capability affected
- Capability 3 - Auditable generation: the emitted SHA-256 fingerprint now verifies the exact diff payload returned by `diff_preview`.
- Capability 4 - Operator-first control surface: `diff_preview` now exposes a stable CLI-first surface with a deterministic JSON/text contract.

### Routing/provider impact note
- None. This change only affects local diff-preview output formatting, verification metadata, and focused command-contract test coverage; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` for the approved `tests/unit/test_diff_preview.py` exception only; no policy or integrator-locked files were edited.
