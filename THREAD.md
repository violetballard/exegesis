# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual `codex/feat-commands` branch tip after the `20260429T032835Z` reviewer-fix pass.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Current Effective Diff From Previous Anchor

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

`scripts/scope-check.sh` is included as a cleanup-only gate-policy file because this fixer pass removes prior scope-policy additions from the final branch state.

## Shared / Approval Notes

- Lane-owned implementation edits: `src/qual/commands/**`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval edits: YES.
- Integrator-locked edits: NO.
- Gate-policy cleanup edits: YES, limited to removing prior `scripts/scope-check.sh` scope-policy additions from the final branch state.
- Gate-policy approval / risk rationale: approved as a cleanup-only reviewer fix; it narrows the final branch policy surface and `scripts/scope-check.sh` is not listed as integrator-locked in `THREAD_OWNERSHIP.md`.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`.

## Canonical Demo-Path Mapping

- This command contract hardening makes the CLI smoke path more real for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by guaranteeing parser-visible tokens stay aligned with the command catalog before the contract is returned.

## Reviewer Packet `20260429T032835Z` Fix Satisfaction

1. One review basis is used: the actual final `codex/feat-commands` branch tip, not a narrow historical implementation slice.
2. The complete effective changed-file list from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` is named, including `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. `scripts/scope-check.sh` is documented as cleanup-only gate-policy accounting, with explicit rationale and no integrator-locked claim.
4. Ownership accounting separates approved shared-by-approval tests from integrator-locked edits.
5. Per-task demo-path mapping names project open, retrieval/context basket, patch preview/apply/reject, and export/handoff.
6. Final required gate results for the current reviewer packet are recorded in `THREAD_PACKET.md`.
