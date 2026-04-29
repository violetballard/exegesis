# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual `codex/feat-commands` branch tip after the `20260429T024425Z` reviewer-fix pass.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Shared / Approval Notes

- Lane-owned implementation edits: `src/qual/commands/**`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Shared-by-approval edits: YES.
- Integrator-locked edits: NO.
- Gate-policy edits: NO.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`.

## Canonical Demo-Path Mapping

- This command contract hardening makes the CLI smoke path more real for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by guaranteeing parser-visible tokens stay aligned with the command catalog before the contract is returned.

## Reviewer Packet `20260429T024425Z` Fix Satisfaction

1. The handoff now uses one truthful review basis: the actual `codex/feat-commands` branch tip, including post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation and test commits.
2. `command_cli_contract()` validates the full parser-visible CLI surface before returning the contract: exact tokens, lookup-table shape and order, grouped parser surface, declared surface, and canonical command order.
3. Focused tests cover same-canonical parser drift where canonical names still match, including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`, plus token additions, removals, ordering drift, and lookup-table drift.
4. The task list in `THREAD_PACKET.md` maps each completed task to the protected canonical demo-path command steps.
5. Ownership accounting separates approved shared-by-approval tests from integrator-locked edits; integrator-locked edits are `NO`.
6. Final required gate results are recorded in `THREAD_PACKET.md`.
